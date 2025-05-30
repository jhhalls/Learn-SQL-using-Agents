import sqlparse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from connection import engine

# def validate_sql(sql_query):
#     # Simple validation to ensure it's a SELECT query and prevent any DDL commands
#     parsed = sqlparse.parse(sql_query)
#     for stmt in parsed:
#         if stmt.get_type() != 'SELECT':
#             raise ValueError("Only SELECT queries are allowed!")
#     return sql_query


def validate_sql(sql_query):
    sql_query = sql_query.strip()  # Remove leading/trailing spaces
    parsed = sqlparse.parse(sql_query)
    
    for stmt in parsed:
        stmt_type = stmt.get_type()
        print(f"\nDetected statement type: {stmt_type}")  # Debug print

        if stmt_type == 'UNKNOWN':
            # fallback check
            if not sql_query.upper().startswith("SELECT"):
                raise ValueError("Only SELECT queries are allowed!")
        elif stmt_type != 'SELECT':
            raise ValueError("Only SELECT queries are allowed!")
        
    return sql_query


# def get_statement_type(query):
#     parsed = sqlparse.parse(query)
#     if not parsed:
#         return "UNKNOWN"
    
#     statement = parsed[0]
#     for token in statement.tokens:
#         if token.ttype is sqlparse.tokens.DML:
#             return token.value.upper()
#     return "UNKNOWN"

# def validate_sql(query):
#     stmt_type = get_statement_type(query)
#     print(f"Detected statement type: {stmt_type}")
    
#     if stmt_type != "SELECT":
#         raise ValueError("Only SELECT queries are allowed!")
    
#     return query  # Query is valid


def execute_sql(sql_query):
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = result.fetchall()
            return rows
    except SQLAlchemyError as e:
        return f"Error: {str(e)}"