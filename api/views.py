from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from .models import User, CompanyProfile, JobSeekerProfile, Job, Application, Notification
from .serializers import (
    UserSerializer, CompanyProfileSerializer, JobSeekerProfileSerializer,
    JobSerializer, ApplicationSerializer, NotificationSerializer
)

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'category', 'location']

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user)

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Employer':
            return Application.objects.filter(job__employer=user)
        return Application.objects.filter(seeker=user)

    def perform_create(self, serializer):
        serializer.save(seeker=self.request.user)
        # Notify Employer
        job = serializer.validated_data['job']
        Notification.objects.create(
            user=job.employer,
            message=f"New application received for {job.title} from {self.request.user.username}",
            link=f"/dashboard/applications/" # Adjust as needed
        )

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
