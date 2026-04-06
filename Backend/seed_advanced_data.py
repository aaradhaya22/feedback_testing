import os
import django
from django.db import connection
import random

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
            teachers = [
                "Rajesh Sharma", "Amit Verma", "Priya Singh", "Neha Gupta", "Ankit Patel", 
                "Rahul Mishra", "Pooja Yadav", "Sandeep Kumar", "Kavita Joshi", "Vivek Agarwal", 
                "Nitin Saxena", "Deepak Choudhary", "Shweta Jain", "Manish Tiwari", "Ritu Saxena", 
                "Abhishek Srivastava", "Sneha Kulkarni", "Rohit Mehta", "Anjali Deshmukh", "Kunal Bansal", 
                "Harsh Vardhan", "Meenakshi Iyer", "Arjun Nair", "Pankaj Tripathi", "Sunita Reddy"
            ]
            
            teacher_values = []
            for i, name in enumerate(teachers, 1):
                t_id = f"T{i:03d}"
                designation = random.choice(["Professor", "Assistant Professor", "Associate Professor"])
                teacher_values.append(f"('{t_id}', '{name}', '{designation}')")
                
            cursor.execute(f'''
                INSERT INTO faculty_teacher ("TeacherID", "FullName", "Designation")
                VALUES {", ".join(teacher_values)}
                ON CONFLICT DO NOTHING;
            ''')

            print("Inserting Subjects...")
            # Data format: SubjectCode, SubjectName, Semester, Branch
            subjects_data = []
            
            # CS/IT/DS/CSIT/CY subjects
            cs_branches = ['CS', 'IT', 'DS', 'CSIT', 'CY']
            cs_sems = {
                3: ["Data Structures", "Digital Logic Design", "Discrete Mathematics", "Object Oriented Programming", "Computer Organization & Architecture"],
                4: ["Database Management Systems", "Operating Systems", "Design & Analysis of Algorithms", "Software Engineering", "Computer Networks"],
                5: ["Artificial Intelligence", "Machine Learning", "Web Development", "Data Mining", "Microprocessors & Microcontrollers"],
                6: ["Cloud Computing", "Big Data Analytics", "Cyber Security", "Compiler Design", "Internet of Things"]
            }
            
            code_counter = 100
            for branch in cs_branches:
                for sem, sub_list in cs_sems.items():
                    for i, sub in enumerate(sub_list, 1):
                        subjects_data.append(f"('{branch}{sem}0{i}', '{sub}', {sem}, '{branch}')")
            
            # ME subjects
            me_sems = {
                3: ["Thermodynamics", "Fluid Mechanics", "Strength of Materials", "Manufacturing Process", "Engineering Mathematics III"],
                4: ["Theory of Machines", "Heat Transfer", "Machine Drawing", "Materials Engineering", "Industrial Engineering"],
                5: ["Machine Design", "Automobile Engineering", "Refrigeration & AC", "Mechatronics", "Operations Research"],
                6: ["CAD/CAM", "Robotics", "Power Plant Engineering", "Finite Element Method", "Project Management"]
            }
            for sem, sub_list in me_sems.items():
                for i, sub in enumerate(sub_list, 1):
                    subjects_data.append(f"('ME{sem}0{i}', '{sub}', {sem}, 'ME')")
                    
            # CE subjects
            ce_sems = {
                3: ["Structural Analysis", "Geotechnical Engineering", "Fluid Mechanics", "Surveying", "Engineering Mathematics III"],
                4: ["Concrete Technology", "Environmental Engineering", "Transportation Engineering", "Engineering Geology", "Hydrology"],
                5: ["Design of Steel Structures", "Design of RCC Structures", "Irrigation Engineering", "Construction Planning", "Water Resource Engineering"],
                6: ["Bridge Engineering", "Tunnel Engineering", "Earthquake Engineering", "GIS & Remote Sensing", "Project Management"]
            }
            for sem, sub_list in ce_sems.items():
                for i, sub in enumerate(sub_list, 1):
                    subjects_data.append(f"('CE{sem}0{i}', '{sub}', {sem}, 'CE')")
                    
            # EC subjects
            ec_sems = {
                3: ["Electronic Devices", "Network Theory", "Signals & Systems", "Digital Electronics", "Mathematics III"],
                4: ["Analog Circuits", "Communication Systems", "Control Systems", "Microprocessors", "Electromagnetic Field Theory"],
                5: ["VLSI Design", "Embedded Systems", "Digital Signal Processing", "Microwave Engineering", "Optical Communication"],
                6: ["Wireless Communication", "Satellite Communication", "IoT Systems", "Robotics", "Project"]
            }
            for sem, sub_list in ec_sems.items():
                for i, sub in enumerate(sub_list, 1):
                    subjects_data.append(f"('EC{sem}0{i}', '{sub}', {sem}, 'EC')")

            # Batch insert subjects to avoid too long query string
            # SQLite / Postgres max limit
            for i in range(0, len(subjects_data), 100):
                chunk = subjects_data[i:i+100]
                cursor.execute(f'''
                    INSERT INTO academic_subject ("SubjectCode", "SubjectName", "Semester", "Branch")
                    VALUES {", ".join(chunk)}
                    ON CONFLICT DO NOTHING;
                ''')

            print("Inserting Allocations...")
            # We'll randomly assign teachers to subjects for target sections
            allocations_data = []
            
            # Fetch all subjects to allocate them
            cursor.execute('SELECT "SubjectCode", "Branch", "Semester" FROM academic_subject')
            all_subjects = cursor.fetchall()
            
            for sub_code, branch, sem in all_subjects:
                # Assign 1 random teacher per subject per section (assuming 1 section per branch right now)
                t_id = f"T{random.randint(1, 25):03d}"
                target_year = (sem + 1) // 2
                allocations_data.append(f"('{t_id}', '{sub_code}', '{branch}', {target_year}, {sem}, 1)")

            for i in range(0, len(allocations_data), 100):
                chunk = allocations_data[i:i+100]
                cursor.execute(f'''
                    INSERT INTO academic_allocation ("TeacherID", "SubjectCode", "TargetBranch", "Target_Year", "Target_Semester", "Target_Section")
                    VALUES {", ".join(chunk)}
                ''')

            print("Extensive dummy data inserted successfully.")
    except Exception as e:
        import traceback
        with open("seed_advanced_err.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
            print(f"Error occurred: {e}")

if __name__ == "__main__":
    seed()
