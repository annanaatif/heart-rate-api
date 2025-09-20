🏥 Patient Monitoring System

A Django + Django REST Framework (DRF) based backend system for
monitoring patients’ heart rate data.
This system provides secure role-based access control, device
assignment, data validation, and analytics for patient health
monitoring.

------------------------------------------------------------------------

📁 Project Structure

    patient_monitoring_system/
    ├── manage.py
    ├── requirements.txt
    ├── patient_monitoring/          # Django project
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── monitoring_app/              # Django app
        ├── models.py
        ├── serializers.py
        ├── views.py
        ├── urls.py
        ├── admin.py
        ├── tests.py
        └── migrations/

------------------------------------------------------------------------

🚀 Features

-   👤 Custom User Model with roles: Admin, Staff, Patient
-   🧑‍⚕️ Patient Management – profiles linked to users
-   📟 Device Management – track devices assigned to patients
-   ❤️ Heart Rate Monitoring – patients record and view heart rate data
-   📊 Analytics – min, max, average heart rate over time (daily,
    weekly, monthly)
-   🔐 Security – token authentication, role-based access, data
    isolation
-   ✅ Validation – ensures devices belong to the correct patients

------------------------------------------------------------------------

🛠️ Installation & Setup

1️⃣ Clone the repository

    git clone https://github.com/your-username/patient-monitoring-system.git
    cd patient-monitoring-system

2️⃣ Create & activate a virtual environment

    python -m venv venv
    source venv/bin/activate   # Linux/Mac
    venv\Scripts\activate      # Windows

3️⃣ Install dependencies

    pip install -r requirements.txt

4️⃣ Apply migrations

    python manage.py migrate

5️⃣ Create a superuser (admin)

    python manage.py createsuperuser

6️⃣ Run the server

    python manage.py runserver

Server will start at:
👉 http://127.0.0.1:8000/

------------------------------------------------------------------------

## 🔗 API Endpoints

| Endpoint                                | Method | Purpose                    | Access                          |
|-----------------------------------------|--------|----------------------------|---------------------------------|
| `/api/auth/register/`                   | POST   | Register a new user        | Public                          |
| `/api/auth/login/`                      | POST   | Login and get token        | Public                          |
| `/api/patients/`                        | GET    | List all patients          | Staff / Admin                   |
| `/api/patients/`                        | POST   | Create a new patient       | Admin                           |
| `/api/patients/<id>/`                   | GET    | Retrieve patient details   | Staff / Admin / Patient (own)   |
| `/api/patients/<id>/`                   | PUT    | Update patient details     | Admin                           |
| `/api/patients/<id>/`                   | DELETE | Delete a patient           | Admin                           |
| `/api/heart-rate/`                      | GET    | List heart rate data       | Patient (own) / Staff / Admin   |
| `/api/heart-rate/`                      | POST   | Submit heart rate data     | Patient (own) / Admin           |
| `/api/patients/<id>/heart-rate-stats/`  | GET    | Get heart rate statistics  | Patient (own) / Staff / Admin   |
| `/api/devices/`                         | GET    | List all devices           | Staff / Admin                   |
| `/api/devices/`                         | POST   | Register new device        | Admin                           |
| `/api/devices/<id>/`                    | GET    | Retrieve device details    | Staff / Admin                   |
| `/api/devices/<id>/`                    | PUT    | Update device info         | Admin                           |
| `/api/devices/<id>/`                    | DELETE | Remove a device            | Admin                           |

------------------------------------------------------------------------

🧪 Running Tests

Run the automated test suite:

    python manage.py test

Tests cover: - ✅ User registration & login - ✅ Permissions &
role-based access - ✅ Heart rate data validation - ✅ Device ownership
validation

------------------------------------------------------------------------

⚙️ Configuration

REST Framework Settings (in settings.py)

    REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

------------------------------------------------------------------------

📊 Data Flow

1.  Device records patient’s heart rate.
2.  API Client sends a POST request with data.
3.  Serializer validates data & links it to patient/device.
4.  View checks role-based permissions.
5.  Model saves valid data to DB.
6.  Response returns JSON with the result.

------------------------------------------------------------------------

📂 Example Postman Collection

Copy the JSON below into a file (e.g., postman_collection.json) or
import directly into Postman.

    {
      "info": {
        "name": "Patient Monitoring System API",
        "_postman_id": "12345678-abcd-efgh-ijkl-1234567890ab",
        "description": "Postman collection for Patient Monitoring System APIs",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
      },
      "item": []
    }

------------------------------------------------------------------------

💡 Design Philosophy

-   🔐 Security First – role-based permissions & patient data isolation
-   ⚡ Smart Defaults – auto-assign patient where possible
-   📈 Analytics Ready – built-in heart rate statistics
-   🔄 Extensible – can be extended for more vitals (BP, SpO₂, etc.)

------------------------------------------------------------------------

👨‍💻 Tech Stack

-   Backend: Django, Django REST Framework
-   Database: SQLite (default), PostgreSQL (production-ready)
-   Auth: DRF Token Authentication
-   Testing: Django TestCase & DRF APITestCase
-   Deployment: Gunicorn / Nginx / Docker (optional)

------------------------------------------------------------------------
