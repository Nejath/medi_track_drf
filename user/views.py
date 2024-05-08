from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics,mixins
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .permissions import IsPatientUser
from rest_framework_simplejwt.views import TokenObtainPairView
from datetime import datetime, timedelta
# Create your views here.


class UserloginView(APIView):
    serializer_class = UserTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                # Perform any additional logic if needed
                return Response({"status": 1, "data": serializer.validated_data}, status=status.HTTP_200_OK)
            else:
                return Response({"status": 0, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": 0, "errors": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class PatientRegistrationView(APIView):
    serializer_class = PatientSerializer
    def post(self, request, *args, **kwargs):
        try:
            serializer = PatientSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": 1, "message": "Patient registered successfully."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"status": 0, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": 0, "errors": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  


class HospitalListAPIView(APIView):
    # permission_classes = [IsAuthenticated,IsPatientUser]
    def get(self, request, *args, **kwargs):
        try:

            hospitals = Hospital.objects.all().order_by('name')
            serializer = AllHospitalSerializer(hospitals, many=True)
            return Response({"status":1,"data":serializer.data}, status=status.HTTP_200_OK)
        except Hospital.DoesNotExist:
            return Response({"status":0,"errors":"Hospitals does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        

class DoctorListofHospitalAPIView(APIView):
    # permission_classes = [IsAuthenticated,]
    def get(self, request, hospital_id, *args, **kwargs):
        try:
            doctors = Doctor.objects.filter(hospital_and_department__hospital=hospital_id)
            serializer = DoctorsSerializer(doctors,many=True)
            return Response({"status":1,"data":serializer.data}, status=status.HTTP_200_OK)
        except Doctor.DoesNotExist:
            return Response({"status":0,"errors":"Doctors does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
class DepartmentListofHospitalAPIView(APIView):
    # permission_classes = [IsAuthenticated,]
    def get(self, request, hospital_id, *args, **kwargs):
        try:
            department = Department.objects.filter(hospital=hospital_id)
            serializer = DepartmentSerializer(department,many=True)
            return Response({"status":1,"data":serializer.data}, status=status.HTTP_200_OK)
        except Department.DoesNotExist:
            return Response({"status":0,"errors":"Doctors does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
class DoctorListofDepartmentAPIView(APIView):
    # permission_classes = [IsAuthenticated,]
    def get(self, request, department_id, *args, **kwargs):
        try:
            doctors = Doctor.objects.filter(hospital_and_department=department_id)
            serializer = DoctorsSerializer(doctors,many=True)
            return Response({"status":1,"data":serializer.data}, status=status.HTTP_200_OK)
        except Doctor.DoesNotExist:
            return Response({"status":0,"errors":"Doctors does not exist."}, status=status.HTTP_404_NOT_FOUND)




class DoctorDetailAPIView(APIView):
    # permission_classes = [IsAuthenticated,]
    def get(self, request, doctor_id, *args, **kwargs):
        try:
           
            doctor = Doctor.objects.get(pk=doctor_id)
            
            serializer = DoctorsSerializer(doctor)
            return Response({"status":1,"data":serializer.data}, status=status.HTTP_200_OK)
        except Doctor.DoesNotExist:
            return Response({"status":0,"errors":"Doctor not found."}, status=status.HTTP_404_NOT_FOUND)



class AvailableSlotsAPIView(APIView):
    # permission_classes = [IsAuthenticated,]
    def get(self, request, doctor_id, day, *args, **kwargs):
        try:
            # Get all time slots for the given day and doctor
            all_time_slots = [ {"time": choice[0], "is_booked": False} for choice in TIME_CHOICES ]

            # Mark booked time slots as "is_booked: True"
            booked_slots = Appointment.objects.filter(doctor_id=doctor_id, day=day)
            for booked_slot in booked_slots:
                time = booked_slot.time
                for slot in all_time_slots:
                    if slot["time"] == time:
                        slot["is_booked"] = True

            serializer = AvailableSlotsSerializer(all_time_slots, many=True)
            return Response({"status":1,"data":serializer.data}, status=status.HTTP_200_OK)
        except :
            return Response({"status":0,"error":"something went wrong"}, status=status.HTTP_404_NOT_FOUND)


class BookAppointmentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsPatientUser]
    def post(self, request,doctor_id, *args, **kwargs):
        try:
            serializer = AppointmentSerializer(data=request.data)
            if serializer.is_valid():
                # Check if the requested time slot is available
                # doctor = serializer.validated_data['doctor']
                # doctor_id = serializer.validated_data['doctor'].id
                doctor=Doctor.objects.get(id=doctor_id)
                
                day = serializer.validated_data['day']
                time = serializer.validated_data['time']
                
                if Appointment.objects.filter(doctor_id=doctor, day=day, time=time).exists():
                    return Response({"status": 0,"data":"This appointment slot is already booked."}, status=status.HTTP_400_BAD_REQUEST)
               
                # If the slot is available, save the appointment
                #hospital=doctor.hospital_and_department.hospital
                serializer.save(user=request.user.patient,doctor=doctor)
                return Response({"status": 1, "data": serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"status": 0, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"status": 0,"error":"Something went wrong"}, status=status.HTTP_404_NOT_FOUND)
        
        
        
class ListPatientAppointmentsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsPatientUser]
    def get(self, request, *args, **kwargs):
        try:
            appointments = Appointment.objects.filter(user=request.user.patient).order_by('-time_created')
            
            serializer = AppointmentviewSerializer(appointments, many=True)
            
            return Response({"status":1,"data":serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({"status":0,"error":"Something went wrong"}, status=status.HTTP_404_NOT_FOUND)



class PatientAppointmentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get(self, request, appointment_id, *args, **kwargs):
        try:
           
            appointment = Appointment.objects.get(pk=appointment_id)
            
            serializer = AppointmentviewSerializer(appointment)
            return Response({"status":1,"data":serializer.data}, status=status.HTTP_200_OK)
        except Appointment.DoesNotExist:
            return Response({"status":0,"errors":"Appointment not found."}, status=status.HTTP_404_NOT_FOUND)




class CancelAppointmentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsPatientUser]
    def delete(self, request, appointment_id, *args, **kwargs):
        # Check if the appointment exists
        try:
            appointment = Appointment.objects.get(id=appointment_id, user=request.user.patient)
        except Appointment.DoesNotExist:
            return Response({"status":0,"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        # Delete the appointment
        appointment.delete()
        return Response({"status":1,"success": "Appointment canceled successfully."}, status=status.HTTP_204_NO_CONTENT)



class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated,IsPatientUser]

    def get(self, request, *args, **kwargs):
        try:
            user_profile = Patient.objects.get(user=request.user)
            serializer = PatientSerializer(user_profile)
            return Response({"status":1,"data":serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({"status":0,"data":"Something went wrong"}, status=status.HTTP_404_NOT_FOUND)
        
        
        
        
# alerts
class Get_appointments_alerts(APIView):
    permission_classes = [IsAuthenticated,IsPatientUser]
    def get(self, request, *args, **kwargs):
        
        try:
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            
            appointments_between_today_and_tomorrow = Appointment.objects.filter(              
                day__gte=today,
                day__lte=tomorrow,
                user=request.user.patient              
                ).order_by('day')
            response_data = []
           
            if appointments_between_today_and_tomorrow:
                for appointment in appointments_between_today_and_tomorrow:
                    if appointment.day==today:
                        day="today"
                    else:
                        day="tommorow"                        
                    response_data.append({
                        "message": f"Your appointment with Dr. {appointment.doctor.name} on {appointment.day}({day}) at {appointment.doctor.hospital_and_department.hospital} at {appointment.time}",                   
                    })
                
                serializer = AppointmentAlertSerializer(response_data, many=True)               
                return Response({"status":1,"data":serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"status":1,"data":response_data}, status=status.HTTP_200_OK)
        except:
            return Response({"status":0,"error":"Something went wrong"}, status=status.HTTP_404_NOT_FOUND)

        