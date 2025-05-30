sql_agent/
│
├── config/
│   └── db_config.py           # Database connection settings (MySQL config here)
│
├── models/
│   └── schema_reflector.py    # Code to fetch schema (tables/columns) dynamically
│
├── services/
│   ├── llm_query_generator.py # Code to call LLM (OpenAI, etc.) to generate SQL
│   └── query_executor.py      # Code to validate and execute SQL queries
│
├── utils/
│   ├── sql_validator.py       # Code to validate (safe) SQL queries
│   └── prompt_builder.py      # Build smart prompts for LLM using schema
│
├── logs/
│   └── app.log                # Application logs (auto-generated)
│
├── main.py                    # Entry point to run your SQL agent
│
├── requirements.txt           # Python packages required
│
└── README.md                  # Project documentation


<!-- High Level Architecture -->
+----------------+
| User Interface |
+----------------+
        |
        v
+---------------------------+
| Query Generator (LLM call) |
+---------------------------+
        |
        v
+----------------------+
| SQL Validator/Sandbox |
+----------------------+
        |
        v
+----------------+
| DB Connector   |
+----------------+
        |
        v
+-----------------+
| Results Renderer |
+-----------------+