from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Patient, HeartRateData, Device

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name', 'user_type', 'phone_number')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
                
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

class PatientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    phone_number = serializers.CharField(source='user.phone_number')
    
    class Meta:
        model = Patient
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 
                 'date_of_birth', 'gender', 'address', 'emergency_contact', 'medical_history')
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            phone_number=user_data.get('phone_number', ''),
            password=user_data.get('password', 'default_password'),
            user_type='patient'
        )
        patient = Patient.objects.create(user=user, **validated_data)
        return patient
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'

class HeartRateDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeartRateData
        fields = ('id', 'device', 'patient', 'heart_rate', 'recorded_at', 'created_at')
        read_only_fields = ('patient', 'created_at')
    
    def validate(self, attrs):
        device = attrs.get('device')
        patient = self.context['request'].user.patient_profile if hasattr(self.context['request'].user, 'patient_profile') else None
        
        if device and patient and device.patient != patient:
            raise serializers.ValidationError({"device": "This device does not belong to the patient."})
        
        return attrs