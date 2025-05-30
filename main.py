from sql_agent.connection import get_schema_info
from sql_agent.services.llm_query_generator import generate_sql
from sql_agent.services.query_executor_validator import validate_sql, execute_sql
from sql_agent.services.llm_query_generator import explain_sql_query
from sql_agent.connection import engine
from dotenv import load_dotenv
load_dotenv()



def main():
    # Get schema info from the database
    schema_info = get_schema_info()

    # Ask user for natural language query
    user_query = input("\nEnter your query: ")

    # Generate SQL using GPT-4
    sql_query = generate_sql(user_query, schema_info)
    print("=="*50)
    print("\nGenerated SQL Query:\n", sql_query)
    print("=="*50)

    # Validate the SQL query
    try:
        validated_query = validate_sql(sql_query)
    except ValueError as e:
        print(f"Validation Error: {e}")
        return

    # Execute the query
    results = execute_sql(validated_query)
    print("\nQuery Results:", results)

     # Explain the generated SQL
    sql_explanation = explain_sql_query(sql_query)
    print("\nSQL Query Explanation:\n", sql_explanation)


if __name__ == "__main__":
    main()