from rest_framework import status, permissions, generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from .models import User, Patient, Device, HeartRateData
from .serializers import (UserRegistrationSerializer, UserLoginSerializer, 
                         PatientSerializer, DeviceSerializer, HeartRateDataSerializer)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # If serializer.save() returns a list, get the first user
        if isinstance(user, list):
            user = user[0]
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'user_type': user.user_type
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        validated_data = serializer.validated_data
        user = None
        if isinstance(validated_data, dict) and 'user' in validated_data:
            user = validated_data['user']
        if user is None:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'user_type': user.user_type
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientListCreateView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender']
    search_fields = ['user__first_name', 'user__last_name', 'user__username']
    ordering_fields = ['user__first_name', 'user__last_name', 'created_at']
    ordering = ['user__first_name']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return super().get_permissions()

class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return super().get_permissions()

class DeviceListCreateView(generics.ListCreateAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'patient']
    search_fields = ['device_id', 'patient__user__username']

class DeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

class HeartRateDataListCreateView(generics.ListCreateAPIView):
    serializer_class = HeartRateDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['device']
    ordering_fields = ['recorded_at', 'created_at', 'heart_rate']
    ordering = ['-recorded_at']
    
    def get_queryset(self):
        user = self.request.user
        patient_profile = getattr(user, 'patient_profile', None)
        if user.is_authenticated and patient_profile is not None:
            return HeartRateData.objects.filter(patient=patient_profile)
        elif user.is_authenticated and (user.is_staff or user.is_superuser):
            return HeartRateData.objects.all()
        return HeartRateData.objects.none()
    
    def perform_create(self, serializer):
        try:
            patient = Patient.objects.get(user=self.request.user)
            serializer.save(patient=patient)
        except Patient.DoesNotExist:
            serializer.save()

class PatientHeartRateStatsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        patient_id = kwargs.get('patient_id')
        
        user = request.user
        if hasattr(user, 'patient_profile') and user.patient_profile.id != patient_id:
            return Response({"error": "You can only view your own data."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response({"error": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)
        
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)
        
        all_data = HeartRateData.objects.filter(patient=patient)
        today_data = all_data.filter(recorded_at__gte=today_start)
        week_data = all_data.filter(recorded_at__gte=week_start)
        month_data = all_data.filter(recorded_at__gte=month_start)
        
        def calculate_stats(queryset):
            heart_rates = list(queryset.values_list('heart_rate', flat=True))
            if not heart_rates:
                return None
            
            return {
                'min': min(heart_rates),
                'max': max(heart_rates),
                'avg': sum(heart_rates) / len(heart_rates),
                'count': len(heart_rates)
            }
        
        stats = {
            'all_time': calculate_stats(all_data),
            'month': calculate_stats(month_data),
            'week': calculate_stats(week_data),
            'today': calculate_stats(today_data),
        }
        
        return Response(stats)