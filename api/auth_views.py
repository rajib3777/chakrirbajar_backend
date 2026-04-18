from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import User, CompanyProfile, JobSeekerProfile
from .serializers import UserSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = request.data.get('password')
        role = request.data.get('role', 'JobSeeker')
        mobile = request.data.get('mobile')
        
        if not mobile:
            return Response({'error': 'Mobile number is mandatory.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(mobile=mobile).exists():
            return Response({'error': 'Mobile number already registered.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=password,
            role=role,
            mobile=mobile
        )
        
        # Create profile based on role
        if role == 'Employer':
            CompanyProfile.objects.create(user=user, company_name=request.data.get('company_name', f"{user.username}'s Company"))
        else:
            JobSeekerProfile.objects.create(user=user)
            
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        login_id = request.data.get('login_id') # Changed from username to login_id
        username = request.data.get('username') # Fallback for old clients
        password = request.data.get('password')
        
        target_id = (login_id or username or '').strip()
        user = None

        if target_id:
            # Try username first
            user = authenticate(username=target_id, password=password)
            if not user:
                # Try email
                try:
                    u = User.objects.get(email=target_id)
                    user = authenticate(username=u.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if not user:
                # Try mobile
                try:
                    u = User.objects.get(mobile=target_id)
                    user = authenticate(username=u.username, password=password)
                except User.DoesNotExist:
                    pass
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            })
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
