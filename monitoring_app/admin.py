from django.contrib import admin
from .models import User, Patient, Device, HeartRateData

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'gender')
    list_filter = ('gender',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'patient', 'status', 'registered_at', 'last_activity')
    list_filter = ('status',)
    search_fields = ('device_id', 'patient__user__username')

@admin.register(HeartRateData)
class HeartRateDataAdmin(admin.ModelAdmin):
    list_display = ('patient', 'device', 'heart_rate', 'recorded_at')
    list_filter = ('recorded_at',)
    search_fields = ('patient__user__username', 'device__device_id')