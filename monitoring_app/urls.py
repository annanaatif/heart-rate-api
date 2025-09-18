from django.urls import path, include
from . import views

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    
    # Patient endpoints
    path('patients/', views.PatientListCreateView.as_view(), name='patient-list'),
    path('patients/<int:pk>/', views.PatientDetailView.as_view(), name='patient-detail'),
    
    # Heart rate endpoints
    path('heart-rate/', views.HeartRateDataListCreateView.as_view(), name='heart-rate-list'),
    path('patients/<int:patient_id>/heart-rate-stats/', views.PatientHeartRateStatsView.as_view(), name='patient-heart-rate-stats'),
    
    # Device endpoints
    path('devices/', views.DeviceListCreateView.as_view(), name='device-list'),
    path('devices/<int:pk>/', views.DeviceDetailView.as_view(), name='device-detail'),
]