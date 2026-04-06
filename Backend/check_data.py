import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feedbacksystem.settings')
django.setup()

def check_data():
    with connection.cursor() as cursor:
        with open("data_output_safe.txt", "w", encoding="utf-8") as f:
            cursor.execute("SELECT * FROM faculty_teacher;")
            f.write(f"Faculty: {cursor.fetchall()}\n")
            cursor.execute("SELECT * FROM academic_subject;")
            f.write(f"Subjects: {cursor.fetchall()}\n")
            cursor.execute("SELECT * FROM academic_allocation;")
            f.write(f"Allocations: {cursor.fetchall()}\n")

if __name__ == "__main__":
    check_data()
