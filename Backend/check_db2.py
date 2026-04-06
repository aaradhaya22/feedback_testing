import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feedbacksystem.settings')
django.setup()

def check_stuff():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM django_migrations WHERE app='feedback_app'")
        print("Migrations for feedback_app:", cursor.fetchall())

        try:
            cursor.execute("SELECT * FROM academic_allocation")
            print("Successfully selected from academic_allocation! Columns are:")
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='academic_allocation'")
            print(cursor.fetchall())
        except Exception as e:
            print("ERROR testing academic_allocation:", e)
        
if __name__ == "__main__":
    check_stuff()
