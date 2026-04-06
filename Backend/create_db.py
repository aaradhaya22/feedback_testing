import psycopg
import os
from dotenv import load_dotenv

load_dotenv()
try:
    with psycopg.connect(
        dbname="postgres",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        autocommit=True
    ) as conn:
        conn.execute(f'CREATE DATABASE "{os.getenv("DB_NAME")}"')
        print("Database created successfully!")
except Exception as e:
    print("Error:", e)
