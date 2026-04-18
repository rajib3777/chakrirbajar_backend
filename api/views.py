import json
from rest_framework import viewsets, permissions, status, filters, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        user = self.request.user
        queryset = Job.objects.filter(is_active=True).order_by('-created_at')
        
        # If 'mine' query param is present and user is authenticated employer
        if self.request.query_params.get('mine') == 'true' and user.is_authenticated and user.role == 'Employer':
            return Job.objects.filter(employer=user).order_by('-created_at')
            
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'Employer':
             raise serializers.ValidationError("Only Employers can post jobs.")
        
        # Check if company profile is complete
        try:
            profile = user.company_profile
            if not profile.company_name or not profile.description or not profile.location:
                raise serializers.ValidationError("Please complete your Company Profile (Name, Description, Location) before posting a job.")
        except CompanyProfile.DoesNotExist:
            raise serializers.ValidationError("Employer must have a company profile.")
            
        serializer.save(employer=user)

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Employer':
            return Application.objects.filter(job__employer=user).order_by('-applied_at')
        return Application.objects.filter(seeker=user).order_by('-applied_at')

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'JobSeeker':
            raise serializers.ValidationError("Only Job Seekers can apply for jobs.")
            
        # Check if job seeker profile is complete
        try:
            profile = user.seeker_profile
            if not profile.resume:
                raise serializers.ValidationError("You must upload your CV (Resume) before applying for a job.")
            if not profile.nid_card:
                raise serializers.ValidationError("You must upload your NID Card for verification before applying.")
        except JobSeekerProfile.DoesNotExist:
            raise serializers.ValidationError("User must have a job seeker profile.")

        serializer.save(seeker=user)
        # Notify Employer
        job = serializer.validated_data['job']
        Notification.objects.create(
            user=job.employer,
            message=f"New application received for {job.title} from {user.username}",
            link=f"/dashboard/applicants/"
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == 'Shortlisted':
            message = f"অভিনন্দন! আপনি '{instance.job.title}' চাকরির জন্য শর্টলিস্টেড হয়েছেন।"
            Notification.objects.create(
                user=instance.seeker,
                message=message,
                link=f"/profile/" # Seeker should check their profile for status
            )

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def bulk_shortlist(self, request):
        application_ids = request.data.get('application_ids', [])
        if not application_ids:
            return Response({"error": "No applications selected."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure IDs are integers
        try:
            application_ids = [int(aid) for aid in application_ids]
        except (ValueError, TypeError):
            return Response({"error": "Invalid application IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        apps = Application.objects.filter(id__in=application_ids, job__employer=request.user)
        count = apps.count()
        
        if count == 0:
            return Response({"error": "No valid applications found for your jobs."}, status=status.HTTP_404_NOT_FOUND)

        # Trigger notifications
        for app in apps:
            Notification.objects.create(
                user=app.seeker,
                message=f"নিয়োগকর্তা আপনাকে {app.job.title} চাকরির জন্য শর্টলিস্ট করেছেন।",
                link="/profile/"
            )
        
        # Atomic update
        apps.update(status='Shortlisted')
        
        return Response({"message": f"{count} applications shortlisted successfully."})

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def bulk_message(self, request):
        application_ids = request.data.get('application_ids', [])
        message = request.data.get('message', '')
        
        if not application_ids or not message:
            return Response({"error": "Applications and message are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            application_ids = [int(aid) for aid in application_ids]
        except (ValueError, TypeError):
            return Response({"error": "Invalid application IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        apps = Application.objects.filter(id__in=application_ids, job__employer=request.user)
        for app in apps:
            Notification.objects.create(
                user=app.seeker,
                message=f"নিয়োগকর্তার বার্তা ({app.job.title}): {message}",
                link="/profile/"
            )
        
        return Response({"message": f"Message sent to {apps.count()} candidates."})

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "notification marked as read"})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"status": "all notifications marked as read"})

class CompanyProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CompanyProfile.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        user = self.request.user
        # Prevent duplicate profile creation (IntegrityError)
        if CompanyProfile.objects.filter(user=user).exists():
            profile = CompanyProfile.objects.get(user=user)
            # If POST is called but profile exists, we treat it as an update
            serializer = self.get_serializer(profile, data=self.request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return
        
        serializer.save(user=user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

class JobSeekerProfileViewSet(viewsets.ModelViewSet):
    serializer_class = JobSeekerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobSeekerProfile.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        user = self.request.user
        # Prevent duplicate profile creation (IntegrityError)
        data = self.request.data.copy()
        for field in ['education', 'experience']:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except (ValueError, TypeError):
                    pass
        
        if JobSeekerProfile.objects.filter(user=user).exists():
            profile = JobSeekerProfile.objects.get(user=user)
            serializer = self.get_serializer(profile, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

    def perform_update(self, serializer):
        data = self.request.data.copy()
        for field in ['education', 'experience']:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except (ValueError, TypeError):
                    pass
        serializer.save(user=self.request.user, **{f: data[f] for f in ['education', 'experience'] if f in data})
