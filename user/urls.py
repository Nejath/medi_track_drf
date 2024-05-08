"""
URL configuration for medi_track project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [

    path('patient-register/', views.PatientRegistrationView.as_view()),
    path('login/', views.UserloginView.as_view()),
    
    
    path('hospital-list/', views.HospitalListAPIView.as_view()),
    path('doctors-list-by-hospital/<int:hospital_id>/',views.DoctorListofHospitalAPIView.as_view()),
    path('department-list-by-hospital/<int:hospital_id>/', views.DepartmentListofHospitalAPIView.as_view()),
    path('doctors-list-by-department/<int:department_id>/', views.DoctorListofDepartmentAPIView.as_view()),
    path('doctor-detal/<int:doctor_id>/', views.DoctorDetailAPIView.as_view()),
    
    path('available-slots/<int:doctor_id>/<str:day>/', views.AvailableSlotsAPIView.as_view(),),

    path('book-appointment/<int:doctor_id>/', views.BookAppointmentAPIView.as_view()),
     
    path('list-patient-appointments/', views.ListPatientAppointmentsAPIView.as_view(),),
    path('appointment-detail/<int:appointment_id>/', views.PatientAppointmentDetailAPIView.as_view(),),
    path('cancel-appointment/<int:appointment_id>/', views.CancelAppointmentAPIView.as_view(),),
    
    path('user-profile/', views.UserProfileAPIView.as_view(),),

    # path('doctor-detail/<int:doctor_id>/', views.DoctorDetailAPIView.as_view(),),
    #alerts
    path('alerts/', views.Get_appointments_alerts.as_view(),),
]
