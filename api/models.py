from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('Employer', 'Employer'),
        ('JobSeeker', 'JobSeeker'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='JobSeeker')
    mobile = models.CharField(max_length=15, blank=True, null=True)

class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=255)
    description = models.TextField()
    website = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)

    def __str__(self):
        return self.company_name

class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seeker_profile')
    bio = models.TextField(blank=True)
    skills = models.TextField(blank=True) # JSON or comma separated
    education = models.JSONField(default=list) # List of dicts
    experience = models.JSONField(default=list) # List of dicts
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Job(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=255)
    salary_range = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100)
    job_type = models.CharField(max_length=50, choices=[('Full-Time', 'Full-Time'), ('Part-Time', 'Part-Time'), ('Remote', 'Remote'), ('Internship', 'Internship')])
    custom_demands = models.JSONField(default=list, blank=True) # Dynamic questions from employer
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    answers = models.JSONField(default=dict) # Answers to custom demands
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Reviewed', 'Reviewed'), ('Shortlisted', 'Shortlisted'), ('Rejected', 'Rejected')], default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
