import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feedbacksystem.settings')
django.setup()

def seed():
    try:
        with connection.cursor() as cursor:
            print("Clearing old data...")
            cursor.execute('TRUNCATE TABLE academic_allocation CASCADE')
            cursor.execute('TRUNCATE TABLE faculty_teacher CASCADE')
            cursor.execute('TRUNCATE TABLE academic_subject CASCADE')

            print("Inserting Teachers...")
            cursor.execute('''
                INSERT INTO faculty_teacher ("TeacherID", "FullName", "Designation")
                VALUES 
                ('T001', 'Dr. Ramesh Kumar', 'Professor'),
                ('T002', 'Dr. Suresh Sharma', 'Professor'),
                ('T003', 'Mr. Amit Patel', 'Assistant Professor'),
                ('T004', 'Ms. Priya Singh', 'Assistant Professor'),
                ('T005', 'Dr. Rakesh Gupta', 'Associate Professor'),
                ('T006', 'Mrs. Neha Verma', 'Assistant Professor'),
                ('T007', 'Mr. Vikram Desai', 'Assistant Professor'),
                ('T008', 'Dr. Anjali Joshi', 'Professor'),
                ('T009', 'Dr. Sanjay Reddy', 'Associate Professor'),
                ('T010', 'Ms. Pooja Mishra', 'Assistant Professor'),
                ('T011', 'Dr. Alok Tiwari', 'Professor'),
                ('T012', 'Mr. Rohan Menon', 'Assistant Professor')
                ON CONFLICT DO NOTHING;
            ''')

            print("Inserting Subjects...")
            cursor.execute('''
                INSERT INTO academic_subject ("SubjectCode", "SubjectName", "Semester", "Branch")
                VALUES 
                -- 3rd Semester
                ('CS301', 'Data Structures', 3, 'CS'),
                ('IT301', 'Data Structures', 3, 'IT'),
                ('CS302', 'Object Oriented Programming', 3, 'CS'),
                ('IT302', 'Object Oriented Programming', 3, 'IT'),
                ('CS303', 'Digital Logic & Electronics', 3, 'CS'),
                ('CS304', 'Computer Organization & Architecture', 3, 'CS'),
                ('CS305', 'Discrete Mathematics', 3, 'CS'),

                -- 4th Semester
                ('CS401', 'Design & Analysis of Algorithms', 4, 'CS'),
                ('IT401', 'Design & Analysis of Algorithms', 4, 'IT'),
                ('CS402', 'Operating System', 4, 'CS'),
                ('IT402', 'Operating System', 4, 'IT'),
                ('CS403', 'Database Management System', 4, 'CS'),
                ('IT403', 'Database Management System', 4, 'IT'),
                ('CS404', 'Theory of Computation', 4, 'CS'),
                ('CS405', 'Software Engineering', 4, 'CS'),

                -- 5th Semester
                ('CS501', 'Computer Networks', 5, 'CS'),
                ('IT501', 'Computer Networks', 5, 'IT'),
                ('CS502', 'Compiler Design', 5, 'CS'),
                ('CS503', 'Artificial Intelligence', 5, 'CS'),
                ('DS501', 'Artificial Intelligence', 5, 'DS'),
                ('CS504', 'Web Technology', 5, 'CS'),
                ('IT504', 'Web Technology', 5, 'IT'),
                ('CS505', 'Distributed Systems & Cloud Computing', 5, 'CS'),

                -- 6th Semester
                ('CS601', 'Machine Learning', 6, 'CS'),
                ('DS601', 'Machine Learning', 6, 'DS'),
                ('CS602', 'Data Mining & Data Analytics', 6, 'CS'),
                ('DS602', 'Data Mining & Data Analytics', 6, 'DS'),
                ('CS603', 'Information Security & Cyber Security', 6, 'CS'),
                ('IT603', 'Information Security & Cyber Security', 6, 'IT'),
                ('CS604', 'Big Data', 6, 'CS'),
                ('DS604', 'Big Data Analytics', 6, 'DS'),
                ('CS605', 'Mobile Computing & IoT', 6, 'CS'),
                ('DS605', 'Deep Learning & Neural Networks', 6, 'DS'),
                ('DS606', 'Natural Language Processing', 6, 'DS')
                ON CONFLICT DO NOTHING;
            ''')

            print("Inserting Allocations...")
            cursor.execute('''
                INSERT INTO academic_allocation ("TeacherID", "SubjectCode", "TargetBranch", "Target_Year", "Target_Semester", "Target_Section")
                VALUES 
                -- 3rd Semester Allocations
                ('T001', 'CS301', 'CS', 2, 3, 1),
                ('T002', 'IT301', 'IT', 2, 3, 1),
                ('T003', 'CS302', 'CS', 2, 3, 1),
                ('T004', 'CS303', 'CS', 2, 3, 1),
                ('T005', 'CS304', 'CS', 2, 3, 1),

                -- 4th Semester Allocations
                ('T006', 'CS401', 'CS', 2, 4, 1),
                ('T007', 'IT401', 'IT', 2, 4, 1),
                ('T008', 'CS402', 'CS', 2, 4, 1),
                ('T009', 'CS403', 'CS', 2, 4, 1),
                ('T010', 'CS404', 'CS', 2, 4, 1),

                -- 5th Semester Allocations
                ('T001', 'CS501', 'CS', 3, 5, 1),
                ('T002', 'CS502', 'CS', 3, 5, 1),
                ('T011', 'DS501', 'DS', 3, 5, 1),
                ('T004', 'CS504', 'CS', 3, 5, 1),
                ('T005', 'CS505', 'CS', 3, 5, 1),

                -- 6th Semester Allocations (Including Data Science)
                ('T008', 'CS601', 'CS', 3, 6, 1),
                ('T008', 'DS601', 'DS', 3, 6, 1),
                ('T009', 'CS602', 'CS', 3, 6, 1),
                ('T009', 'DS602', 'DS', 3, 6, 1),
                ('T012', 'CS603', 'CS', 3, 6, 1),
                ('T007', 'IT603', 'IT', 3, 6, 1),
                ('T011', 'DS604', 'DS', 3, 6, 1),
                ('T010', 'DS605', 'DS', 3, 6, 1),
                ('T011', 'DS606', 'DS', 3, 6, 1);
            ''')

            print("Extensive dummy data inserted successfully.")
    except Exception as e:
        import traceback
        with open("seed_err.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())

if __name__ == "__main__":
    seed()
