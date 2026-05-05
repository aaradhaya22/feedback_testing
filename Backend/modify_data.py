import os
import django
import sys
import math
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feedbacksystem.settings')
django.setup()

from feedback_app.models import Faculty_Teacher, Academic_Subject, Academic_Allocation, Feedback_Response

def _std_dev(values):
    if len(values) < 2: return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5

def generate_column_ratings(target_avg, count, volatile=False):
    """
    Generates 'count' ratings (1-5) that average to target_avg.
    volatile=True uses 1s and 5s to maximize standard deviation.
    """
    target_sum = int(round(target_avg * count))
    
    if volatile:
        # Mix of 1s and 5s
        # 5x + 1(count-x) = target_sum
        # 4x = target_sum - count
        x = (target_sum - count) // 4
        ratings = [5] * x + [1] * (count - x)
        # Adjust remainder to match exact sum
        current_sum = sum(ratings)
        diff = target_sum - current_sum
        while diff > 0:
            for i in range(len(ratings)):
                if ratings[i] < 5:
                    add = min(5 - ratings[i], diff)
                    ratings[i] += add
                    diff -= add
                if diff == 0: break
        while diff < 0:
             for i in range(len(ratings)):
                if ratings[i] > 1:
                    sub = min(ratings[i] - 1, abs(diff))
                    ratings[i] -= sub
                    diff += sub
                if diff == 0: break
    else:
        # Clustered around average
        base = int(target_avg)
        ratings = [base] * count
        current_sum = sum(ratings)
        diff = target_sum - current_sum
        while diff > 0:
            for i in range(len(ratings)):
                if ratings[i] < 5:
                    ratings[i] += 1
                    diff -= 1
                if diff == 0: break
        while diff < 0:
            for i in range(len(ratings)):
                if ratings[i] > 1:
                    ratings[i] -= 1
                    diff += 1
                if diff == 0: break
                
    random.shuffle(ratings)
    return ratings

def main():
    teacher_ids = ['T027', 'T028', 'T029', 'T030', 'T031']
    Feedback_Response.objects.filter(AllocationID__TeacherID__TeacherID__in=teacher_ids).delete()

    ds_subject, _ = Academic_Subject.objects.get_or_create(
        SubjectCode='DS101',
        defaults={'SubjectName': 'Data Structures', 'Semester': 1, 'Branch': 'CSE'}
    )

    # Specific S1-S10 target averages as requested/analyzed
    targets = {
        'T027': [4.8, 4.9, 5.0, 4.8, 5.0, 4.9, 4.9, 5.0, 4.8, 4.7], # Excellent (Low Std)
        'T028': [4.2, 4.1, 4.3, 4.2, 4.4, 4.1, 4.2, 4.3, 4.2, 4.2], # Good (High Std -> Downgraded)
        'T029': [3.5, 3.6, 3.4, 3.5, 3.7, 3.5, 3.6, 3.4, 3.5, 3.5], # Good (Moderate)
        'T030': [1.8, 2.0, 2.1, 1.9, 2.2, 1.8, 2.0, 2.1, 1.9, 2.0], # Need Imp.
        'T031': [2.5, 4.5, 1.5, 3.5, 2.0, 5.0, 1.0, 3.0, 4.0, 2.5]  # Random
    }

    names_dict = {
        'T027': 'Ravindra Choudhary (Excellent)',
        'T028': 'Amit Verma (Good - High Std)',
        'T029': 'Neha Gupta (Good)',
        'T030': 'Vivek Agarwal (Need Imp.)',
        'T031': 'Kunal Bansal (Random)'
    }

    RESPONSE_COUNT = 20
    random.seed(42)

    for tid in teacher_ids:
        teacher, _ = Faculty_Teacher.objects.update_or_create(
            TeacherID=tid,
            defaults={'FullName': names_dict.get(tid, tid), 'Designation': 'Professor'}
        )
        
        allocation, _ = Academic_Allocation.objects.get_or_create(
            TeacherID=teacher,
            SubjectCode=ds_subject,
            TargetBranch='CSE',
            Target_Year=1,
            Target_Semester=1,
            Target_Section=1
        )
        
        # Generate matrix of ratings: rows=responses, cols=questions
        matrix = []
        is_volatile = (tid == 'T028' or tid == 'T031')
        
        for q_idx in range(10):
            col_ratings = generate_column_ratings(targets[tid][q_idx], RESPONSE_COUNT, volatile=is_volatile)
            matrix.append(col_ratings)
            
        # Insert responses
        responses = []
        all_stars = []
        for r_idx in range(RESPONSE_COUNT):
            row = [matrix[q_idx][r_idx] for q_idx in range(10)]
            responses.append(Feedback_Response(
                AllocationID=allocation,
                Q1_Rating=row[0], Q2_Rating=row[1], Q3_Rating=row[2], Q4_Rating=row[3], Q5_Rating=row[4],
                Q6_Rating=row[5], Q7_Rating=row[6], Q8_Rating=row[7], Q9_Rating=row[8], Q10_Rating=row[9],
                Comments="Standardized system test data"
            ))
            all_stars.extend([float(s) for s in row])
            
        Feedback_Response.objects.bulk_create(responses)
        
        avg = sum(all_stars) / len(all_stars)
        std = _std_dev(all_stars)
        print(f"Teacher {tid}: Created {RESPONSE_COUNT} responses. Global Avg={avg:.2f}, Global Std={std:.2f}")

if __name__ == '__main__':
    main()
