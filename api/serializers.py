from rest_framework import serializers
from .models import User, CompanyProfile, JobSeekerProfile, Job, Application, Notification

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'mobile')

class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = '__all__'

class JobSeekerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSeekerProfile
        fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
    employer_company = serializers.CharField(source='employer.company_profile.company_name', read_only=True)
    employer_logo = serializers.ImageField(source='employer.company_profile.logo', read_only=True)

    class Meta:
        model = Job
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
