import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feedbacksystem.settings')
django.setup()

def check_schema():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            ORDER BY table_name, ordinal_position;
        """)
        rows = cursor.fetchall()
        with open("schema.txt", "w", encoding="utf-8") as f:
            for row in rows:
                f.write(f"{row[0]} - {row[1]} ({row[2]})\n")

if __name__ == "__main__":
    check_schema()
