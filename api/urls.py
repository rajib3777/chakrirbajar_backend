from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, auth_views

router = DefaultRouter()
router.register(r'jobs', views.JobViewSet, basename='job')
router.register(r'applications', views.ApplicationViewSet, basename='application')
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'employer-profile', views.CompanyProfileViewSet, basename='employer-profile')
router.register(r'candidate-profile', views.JobSeekerProfileViewSet, basename='candidate-profile')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', auth_views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
]
