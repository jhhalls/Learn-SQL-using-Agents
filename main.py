from connection import get_schema_info
from services.llm_query_generator import generate_sql
from services.query_executor_validator import validate_sql, execute_sql
from services.llm_query_generator import explain_sql_query
from connection import engine

from kivy.clock import Clock
from index import KivyChatApp
import threading

from dotenv import load_dotenv
load_dotenv()



# def main():
#     # Get schema info from the database
#     schema_info = get_schema_info()

#     # Ask user for natural language query
#     user_query = input("\nEnter your query: ")

#     # Generate SQL using GPT-4
#     sql_query = generate_sql(user_query, schema_info)
#     print("=="*50)
#     print("\nGenerated SQL Query:\n", sql_query)
#     print("=="*50)

#     # Validate the SQL query
#     try:
#         validated_query = validate_sql(sql_query)
#     except ValueError as e:
#         print(f"Validation Error: {e}")
#         return

#     # Execute the query
#     results = execute_sql(validated_query)
#     print("\nQuery Results:", results)

#      # Explain the generated SQL
#     sql_explanation = explain_sql_query(sql_query)
#     print("\nSQL Query Explanation:\n", sql_explanation)


# === Callback function for UI ===
# === Callback Handler ===
def handle_user_input(user_query):
    try:
        schema_info = get_schema_info()
        sql_query = generate_sql(user_query, schema_info)
        validated_query = validate_sql(sql_query)
        results = execute_sql(validated_query)
        explanation = explain_sql_query(sql_query)

        Clock.schedule_once(lambda dt: app.display_output(f"[b][color=ffaa00]Generated SQL:[/color][/b] {sql_query}"), 0)
        Clock.schedule_once(lambda dt: app.display_output(f"[b][color=00ff00]Query Results:[/color][/b] {results}"), 0)
        Clock.schedule_once(lambda dt: app.display_output(f"[b][color=ff66cc]Explanation:[/color][/b] {explanation}"), 0)

    except ValueError as ve:
        Clock.schedule_once(lambda dt: app.display_output(f"[b][color=ff0000]Validation Error:[/color][/b] {ve}"), 0)



if __name__ == "__main__":
    app = KivyChatApp(on_submit_callback=handle_user_input)
    app.run()