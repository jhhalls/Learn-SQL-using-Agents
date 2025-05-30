from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import OperationalError
from sql_agent.config import db_config 

# Format for MySQL connection string:
# mysql+pymysql://<username>:<password>@<host>/<database>

# Fetch settings from db_config.py
username = db_config.DB_USER
password = db_config.DB_PASSWORD
host = db_config.DB_HOST
database = db_config.DB_NAME
port = db_config.DB_PORT

# Create the SQLAlchemy engine
engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}')
print("MySQL engine created")

# Reflect the database schema
metadata = MetaData()
metadata.reflect(bind=engine)

# Print available tables
tables = metadata.tables
print("Tables available:", tables.keys())

def get_schema_info():
    schema_info = []
    for table_name, table in tables.items():
        columns = [column.name for column in table.columns]
        schema_info.append(f"\nTable: {table_name} \ncolumns: {', '.join(columns)}")
    return "\n".join(schema_info)

schema = get_schema_info()
print("Schema info:", schema)