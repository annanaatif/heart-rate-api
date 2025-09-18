# tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Patient, Device, HeartRateData

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        
    def test_user_registration(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'staff'
        }
        
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.json())
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')
    
    def test_user_login(self):
        User.objects.create_user(username='testuser', password='testpass123')
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.json())

class PatientAPITests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin', 
            password='adminpass',
            email='admin@example.com'
        )
        
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staffpass',
            user_type='staff'
        )
        
        self.patient_user = User.objects.create_user(
            username='patient',
            password='patientpass',
            user_type='patient'
        )
        
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth='1990-01-01',
            gender='M'
        )
        
        self.client = APIClient()
        self.patient_list_url = reverse('patient-list')
    
    def test_create_patient_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'username': 'newpatient',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'Patient',
            'date_of_birth': '1995-05-05',
            'gender': 'F'
        }
        
        response = self.client.post(self.patient_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 2)
    
    def test_create_patient_as_staff(self):
        self.client.force_authenticate(user=self.staff_user)
        
        data = {
            'username': 'newpatient',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'Patient',
            'date_of_birth': '1995-05-05',
            'gender': 'F'
        }
        
        response = self.client.post(self.patient_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_patients_as_staff(self):
        self.client.force_authenticate(user=self.staff_user)
        
        response = self.client.get(self.patient_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)

class HeartRateDataTests(APITestCase):
    def setUp(self):
        self.patient_user = User.objects.create_user(
            username='patient',
            password='patientpass',
            user_type='patient'
        )
        
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth='1990-01-01',
            gender='M'
        )
        
        self.device = Device.objects.create(
            device_id='DEV001',
            patient=self.patient,
            status='active'
        )
        
        self.heart_rate_url = reverse('heart-rate-list')
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.patient_user)
    
    def test_create_heart_rate_data(self):
        data = {
            'device': self.device.device_id,
            'heart_rate': 72,
            'recorded_at': '2023-05-01T12:00:00Z'
        }
        
        response = self.client.post(self.heart_rate_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(HeartRateData.objects.count(), 1)
        self.assertEqual(HeartRateData.objects.first().heart_rate, 72)
    
    def test_list_heart_rate_data(self):
        HeartRateData.objects.create(
            device=self.device,
            patient=self.patient,
            heart_rate=72,
            recorded_at='2023-05-01T12:00:00Z'
        )
        
        response = self.client.get(self.heart_rate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)