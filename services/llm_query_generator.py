from dotenv import load_dotenv
import os
import openai
from openai import OpenAI
from groq import Groq
load_dotenv()


llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()

if llm_provider == "openai":
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model_name = "gpt-3.5-turbo"  # or "gpt-4-turbo" if you have access
elif llm_provider == "groq":
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    model_name = "llama3-70b-8192"  # or "llama3-70b-8192"
else:
    raise ValueError(f"Unsupported LLM Provider: {llm_provider}")



def generate_sql(user_input, schema_info):
    prompt = f"""
    You are an expert SQL developer. 
    The database schema is as follows:
    {schema_info}
    
    User's Query: "{user_input}"
    
    Please generate a valid SQL query based on the user's input and schema. Ensure it's a SELECT query unless otherwise specified.
    **Return only the SQL code. No explanation. No extra text.**
    """
    
    # response = openai.Completion.create(
    #     model="gpt-4",
    #     prompt=prompt,
    #     max_tokens=150,
    #     n=1,
    #     stop=None,
    #     temperature=0.5
    # )

    # sql_query = response.choices[0].text.strip()

    response = client.chat.completions.create(
        # model="gpt-3.5-turbo",
        model=model_name,
        messages=[
            {"role": "system", "content": "You are an expert SQL developer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=300,
    )

    # sql_query = response.choices[0].message.content.strip()
    sql_query = response.choices[0].message.content.strip().strip("`").strip()

    return sql_query


def explain_sql_query(sql_query):
    prompt = f"""
    You are an expert SQL analyst.
    
    Please explain the following SQL query in simple, clear English so that even a beginner can understand it:
    
    SQL Query:
    {sql_query}
    
    **Important Instructions:**
    - Focus on what the query is trying to retrieve or do.
    - Mention the tables and columns involved.
    - Clearly Explain each and every clause used in the query. first explain the defition and then how it is used.
    - seperate the clauses in the next line
    - If there are conditions (WHERE), mention them briefly.
    - Keep the explanation short and straightforward.
    - At the end, explain the order of execution of the query.
    - In the explanation, include the tables and columns involved in the query.
    - **Return only the explanation. No SQL code, no extra formatting, no apologies.**
    """

    response = client.chat.completions.create(
        model=model_name,   # Same model as your generate_sql function (e.g., "gpt-3.5-turbo" or "gpt-4")
        messages=[
            {"role": "system", "content": "You are an expert SQL analyst and technical writer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=300,
    )

    explanation = response.choices[0].message.content.strip()

    return explanation