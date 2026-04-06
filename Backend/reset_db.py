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
        db = os.getenv("DB_NAME")
        # Terminate other connections if any
        conn.execute(f"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{db}' AND pid <> pg_backend_pid();")
        conn.execute(f'DROP DATABASE IF EXISTS "{db}"')
        conn.execute(f'CREATE DATABASE "{db}"')
        print("Database reset successfully!")
except Exception as e:
    print("Error:", e)
