import sqlparse
import re
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import sqlite3  # Replace with your database connector
from openai import OpenAI  # Assuming OpenAI for LLM integration

class SQLAgent:
    def __init__(self, db_connection, llm_client, schema_info: Dict):
        """
        Initialize the SQL Agent
        
        Args:
            db_connection: Database connection object
            llm_client: LLM client (e.g., OpenAI)
            schema_info: Dictionary containing database schema information
        """
        self.db = db_connection
        self.llm = llm_client
        self.schema = schema_info
        
    def process_query(self, natural_language_query: str) -> Dict:
        """
        Main workflow for processing a natural language query
        """
        # Step 1: Schema Reference & Validation
        schema_context = self._get_relevant_schema(natural_language_query)
        if not schema_context["valid"]:
            return {"success": False, "stage": "schema_validation", "error": schema_context["error"]}
        
        # Step 2: SQL Query Generation
        sql_query = self._generate_sql_query(natural_language_query, schema_context["schema"])
        
        # Step 3: SQL Syntax Validation
        syntax_validation = self._validate_sql_syntax(sql_query)
        if not syntax_validation["valid"]:
            return {"success": False, "stage": "syntax_validation", "error": syntax_validation["error"]}
        
        # Step 4: Intent Validation
        intent_validation = self._validate_intent(natural_language_query, sql_query)
        if not intent_validation["valid"]:
            return {"success": False, "stage": "intent_validation", "error": intent_validation["error"]}
        
        # Step 5: SQL Execution
        execution_result = self._execute_sql(sql_query)
        if not execution_result["success"]:
            return {"success": False, "stage": "execution", "error": execution_result["error"]}
        
        # Step 6: Results Validation
        results_validation = self._validate_results(natural_language_query, execution_result["results"])
        if not results_validation["valid"]:
            return {
                "success": False, 
                "stage": "results_validation", 
                "error": results_validation["error"],
                "suggestion": self._suggest_fix(results_validation["error_type"], sql_query, natural_language_query)
            }
        
        return {
            "success": True,
            "query": sql_query,
            "results": execution_result["results"]
        }
    
    def _get_relevant_schema(self, query: str) -> Dict:
        """
        Extract relevant schema information based on the natural language query
        and validate entity references
        """
        # Use LLM to identify which tables/columns are relevant
        prompt = f"""
        Given the following database schema:
        {self.schema}
        
        And the natural language query:
        "{query}"
        
        Identify which tables and columns are relevant to answering this query.
        """
        
        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        relevant_schema = response.choices[0].message.content
        
        # Validate that all mentioned entities exist in schema
        entities = self._extract_entities(query)
        validation_result = self._validate_entities_in_schema(entities)
        
        return {
            "valid": validation_result["valid"],
            "error": validation_result.get("error", None),
            "schema": relevant_schema
        }
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract potential database entities from natural language query"""
        # Simplified implementation - in practice, use NER or LLM
        words = re.findall(r'\b\w+\b', query.lower())
        return words
    
    def _validate_entities_in_schema(self, entities: List[str]) -> Dict:
        """Validate if extracted entities exist in the schema"""
        # Simplified - real implementation would be more sophisticated
        schema_elements = set()
        for table in self.schema:
            schema_elements.add(table.lower())
            for column in self.schema[table].get("columns", []):
                schema_elements.add(column.lower())
        
        missing_entities = []
        for entity in entities:
            if entity in schema_elements:
                continue
            # Skip common words, only look for potential DB entities
            if entity in ["show", "find", "get", "what", "where", "how", "many", "the", "in", "of"]:
                continue
            missing_entities.append(entity)
        
        if missing_entities:
            return {"valid": False, "error": f"Unknown entities in query: {', '.join(missing_entities)}"}
        return {"valid": True}
    
    def _generate_sql_query(self, query: str, schema_context: str) -> str:
        """Generate SQL query from natural language using LLM"""
        prompt = f"""
        Given the following database schema:
        {schema_context}
        
        Transform this natural language query into SQL:
        "{query}"
        
        Return only the SQL query without any explanation.
        """
        
        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        sql_query = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        sql_query = re.sub(r'```sql|```', '', sql_query).strip()
        
        return sql_query
    
    def _validate_sql_syntax(self, sql_query: str) -> Dict:
        """Validate SQL syntax"""
        try:
            # Use sqlparse to check for valid SQL syntax
            parsed = sqlparse.parse(sql_query)
            if not parsed or not parsed[0].tokens:
                return {"valid": False, "error": "Empty or invalid SQL query"}
            
            # Additional syntax checks
            if "DELETE" in sql_query.upper() or "UPDATE" in sql_query.upper():
                if "WHERE" not in sql_query.upper():
                    return {"valid": False, "error": "DELETE or UPDATE without WHERE clause"}
            
            return {"valid": True}
        except Exception as e:
            return {"valid": False, "error": f"SQL syntax error: {str(e)}"}
    
    def _validate_intent(self, natural_language_query: str, sql_query: str) -> Dict:
        """Validate that the SQL query matches the original intent"""
        prompt = f"""
        Compare the following natural language query and the generated SQL query:
        
        Natural language: "{natural_language_query}"
        SQL: "{sql_query}"
        
        Does the SQL query correctly implement the intent of the natural language query?
        Answer only with YES or NO. If NO, explain why it doesn't match.
        """
        
        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = response.choices[0].message.content
        
        if result.upper().startswith("NO"):
            return {"valid": False, "error": result}
        return {"valid": True}
    
    def _execute_sql(self, sql_query: str) -> Dict:
        """Execute SQL query and return results"""
        try:
            cursor = self.db.cursor()
            cursor.execute(sql_query)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(results, columns=columns)
            
            return {"success": True, "results": df}
        except Exception as e:
            return {"success": False, "error": f"Execution error: {str(e)}"}
    
    def _validate_results(self, query: str, results: pd.DataFrame) -> Dict:
        """Validate that results match expectations"""
        # Check for empty results when not expected
        if results.empty:
            # Use LLM to determine if empty results are expected
            prompt = f"""
            The query "{query}" returned no results.
            Based on the nature of the query, are empty results expected or surprising?
            Answer only with EXPECTED or SURPRISING.
            """
            
            response = self.llm.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            
            if "SURPRISING" in response.choices[0].message.content:
                return {
                    "valid": False, 
                    "error": "Query returned no results unexpectedly", 
                    "error_type": "empty_results"
                }
        
        # Check for too many results
        if len(results) > 1000:
            return {
                "valid": False, 
                "error": f"Query returned too many results ({len(results)})", 
                "error_type": "too_many_results"
            }
        
        return {"valid": True}
    
    def _suggest_fix(self, error_type: str, sql_query: str, natural_language_query: str) -> str:
        """Suggest fixes for common errors"""
        if error_type == "empty_results":
            prompt = f"""
            The following SQL query returned no results:
            "{sql_query}"
            
            Original question: "{natural_language_query}"
            
            Suggest a modified SQL query that might return relevant results by:
            1. Relaxing conditions in WHERE clauses
            2. Checking for case sensitivity issues
            3. Looking for possible typos in table or column references
            """
            
            response = self.llm.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return f"Suggestion: {response.choices[0].message.content}"
            
        elif error_type == "too_many_results":
            return "Consider adding more specific filters to your query using WHERE clauses"
            
        return "No specific suggestion available for this error"


# Example usage
if __name__ == "__main__":
    # Mock database connection
    db_conn = sqlite3.connect(":memory:")
    
    # Mock schema info
    schema = {
        "customers": {
            "columns": ["customer_id", "name", "email", "signup_date"],
            "primary_key": "customer_id"
        },
        "orders": {
            "columns": ["order_id", "customer_id", "order_date", "total_amount"],
            "primary_key": "order_id",
            "foreign_keys": {
                "customer_id": "customers.customer_id"
            }
        }
    }
    
    # Initialize OpenAI client
    client = OpenAI(api_key="your-api-key")
    
    # Create agent
    agent = SQLAgent(db_conn, client, schema)
    
    # Process a query
    result = agent.process_query("Show me all customers who placed orders worth more than $1000 last month")
    
    print(result)