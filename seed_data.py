import os
import django
import sys
import random

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import User, CompanyProfile, JobSeekerProfile, Job, Application, Notification
from django.utils import timezone

def seed_data():
    # 1. Create/Update Superuser
    admin_user, created = User.objects.get_or_create(username='admin')
    admin_user.set_password('admin123')
    admin_user.email = 'admin@chakrirbajar.com'
    admin_user.mobile = '01711111111'
    admin_user.is_superuser = True
    admin_user.is_staff = True
    admin_user.role = 'Employer'
    admin_user.save()
    print(f"Admin user {'created' if created else 'updated'}: admin / admin123")

    # 2. Create/Update Employer
    employer, created = User.objects.get_or_create(username='sheba_solutions', role='Employer')
    employer.set_password('pass123')
    employer.mobile = '01811111111'
    employer.save()
    
    CompanyProfile.objects.update_or_create(
        user=employer,
        defaults={
            "company_name": "Sheba Solutions Ltd.",
            "description": "Leading IT service provider in Bangladesh focusing on Web and AI solutions.",
            "location": "Banani, Dhaka",
            "website": "https://sheba.solutions"
        }
    )
    print("Employer 'sheba_solutions' ensured.")

    # 3. Create Jobs
    jobs_data = [
        {"title": "Senior React Developer", "category": "IT & Software", "salary": "70,000 - 90,000 BDT", "type": "Full-Time"},
        {"title": "Junior Python Dev", "category": "IT & Software", "salary": "35,000 - 45,000 BDT", "type": "Internship"},
        {"title": "UI Designer", "category": "Design", "salary": "25,000 - 35,000 BDT", "type": "Part-Time"},
        {"title": "Marketing Manager", "category": "Marketing", "salary": "50,000 - 70,000 BDT", "type": "Full-Time"},
    ]
    
    created_jobs = []
    for jd in jobs_data:
        job = Job.objects.create(
            employer=employer,
            title=jd['title'],
            description=f"Exciting opportunity for a {jd['title']} at Sheba Solutions.",
            requirements="3+ years of experience, Proficiency in relevant stack.",
            location="Dhaka (Remote)",
            salary_range=jd['salary'],
            category=jd['category'],
            job_type=jd['type']
        )
        created_jobs.append(job)
    print(f"{len(created_jobs)} jobs created for employer.")

    # 4. Create many Job Seekers
    seekers_info = [
        {"name": "rahim_dev", "bio": "Frontend expert", "skills": "React, Vue, Tailwind", "mobile": "01722222221"},
        {"name": "karim_ui", "bio": "Creative thinker", "skills": "Figma, Adobe XD", "mobile": "01722222222"},
        {"name": "saif_python", "bio": "Backend specialist", "skills": "Python, Django, FastAPI", "mobile": "01722222223"},
        {"name": "tonmoy_qa", "bio": "Detail oriented", "skills": "Selenium, Cypress", "mobile": "01722222224"},
        {"name": "anika_marketing", "bio": "Growth hacker", "skills": "SEO, SEM, Copywriting", "mobile": "01722222225"},
        {"name": "sadhin_fullstack", "bio": "Always learning", "skills": "MERN Stack", "mobile": "01722222226"},
    ]

    mock_cv_url = "resumes/mock_resume.txt" # Relative to media root

    for info in seekers_info:
        user, _ = User.objects.get_or_create(username=info['name'], role='JobSeeker')
        user.set_password('pass123')
        user.mobile = info['mobile']
        user.save()
        
        JobSeekerProfile.objects.update_or_create(
            user=user,
            defaults={
                "bio": info['bio'],
                "skills": info['skills'],
                "resume": mock_cv_url # Points to the dummy file we created
            }
        )
        
        # Apply to a few random jobs
        random_jobs = random.sample(created_jobs, k=random.randint(1, 3))
        for j in random_jobs:
            Application.objects.create(
                job=j,
                seeker=user,
                status="Pending"
            )

    print(f"Created {len(seekers_info)} job seekers and their applications.")

if __name__ == "__main__":
    # Clear existing non-admin data for fresh mock
    User.objects.exclude(username='admin').delete()
    seed_data()
    print("Mock data seeding complete!")
