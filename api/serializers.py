from rest_framework import serializers
from .models import User, CompanyProfile, JobSeekerProfile, Job, Application, Notification

def build_abs_url(request, path):
    """Return full absolute URL for a media file, or None if no path."""
    if not path:
        return None
    if request:
        return request.build_absolute_uri(str(path) if not str(path).startswith('/media/') else str(path))
    return f"http://localhost:8000{str(path) if str(path).startswith('/media/') else '/media/' + str(path)}"

class UserSerializer(serializers.ModelSerializer):
    is_employer = serializers.SerializerMethodField()
    is_candidate = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'mobile', 'is_employer', 'is_candidate')

    def get_is_employer(self, obj):
        return obj.role == 'Employer'

    def get_is_candidate(self, obj):
        return obj.role == 'JobSeeker'

class CompanyProfileSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    class Meta:
        model = CompanyProfile
        fields = '__all__'

    def get_logo(self, obj):
        if not obj.logo:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.logo.url) if request else f"http://localhost:8000{obj.logo.url}"

class JobSeekerProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    resume = serializers.SerializerMethodField()
    nid_card = serializers.SerializerMethodField()

    class Meta:
        model = JobSeekerProfile
        fields = ('id', 'bio', 'skills', 'education', 'experience', 'resume', 'nid_card', 'profile_picture')

    def get_profile_picture(self, obj):
        if not obj.profile_picture:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.profile_picture.url) if request else f"http://localhost:8000{obj.profile_picture.url}"

    def get_resume(self, obj):
        if not obj.resume:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.resume.url) if request else f"http://localhost:8000{obj.resume.url}"

    def get_nid_card(self, obj):
        if not obj.nid_card:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.nid_card.url) if request else f"http://localhost:8000{obj.nid_card.url}"

class JobSerializer(serializers.ModelSerializer):
    employer_company = serializers.CharField(source='employer.company_profile.company_name', read_only=True)
    employer_website = serializers.CharField(source='employer.company_profile.website', read_only=True)
    employer_description = serializers.CharField(source='employer.company_profile.description', read_only=True)
    employer_logo = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['employer']

    def get_employer_logo(self, obj):
        try:
            logo = obj.employer.company_profile.logo
            if not logo:
                return None
            request = self.context.get('request')
            return request.build_absolute_uri(logo.url) if request else f"http://localhost:8000{logo.url}"
        except Exception:
            return None

class ApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    seeker_name = serializers.CharField(source='seeker.username', read_only=True)
    seeker_email = serializers.CharField(source='seeker.email', read_only=True)
    seeker_mobile = serializers.CharField(source='seeker.mobile', read_only=True)
    seeker_bio = serializers.CharField(source='seeker.seeker_profile.bio', read_only=True)
    seeker_skills = serializers.CharField(source='seeker.seeker_profile.skills', read_only=True)
    seeker_education = serializers.JSONField(source='seeker.seeker_profile.education', read_only=True)
    seeker_experience = serializers.JSONField(source='seeker.seeker_profile.experience', read_only=True)
    company_name = serializers.CharField(source='job.employer.company_profile.company_name', read_only=True)
    seeker_resume = serializers.SerializerMethodField()
    seeker_nid = serializers.SerializerMethodField()
    seeker_profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ('id', 'job', 'job_title', 'company_name', 'seeker', 'seeker_name', 'seeker_email',
                  'seeker_mobile', 'seeker_resume', 'seeker_bio', 'seeker_skills', 'seeker_education',
                  'seeker_experience', 'seeker_nid', 'seeker_profile_picture', 'answers', 'status', 'applied_at')
        read_only_fields = ('seeker', 'status')

    def _get_media_url(self, field):
        if not field:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(field.url) if request else f"http://localhost:8000{field.url}"

    def get_seeker_resume(self, obj):
        try:
            return self._get_media_url(obj.seeker.seeker_profile.resume)
        except Exception:
            return None

    def get_seeker_nid(self, obj):
        try:
            return self._get_media_url(obj.seeker.seeker_profile.nid_card)
        except Exception:
            return None

    def get_seeker_profile_picture(self, obj):
        try:
            return self._get_media_url(obj.seeker.seeker_profile.profile_picture)
        except Exception:
            return None

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
