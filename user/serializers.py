from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .validators import validate_password_complexity,validate_email,validate_username

class AdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password_complexity])
    email = serializers.EmailField(required=True, validators=[validate_email])
    username = serializers.CharField(required=True, validators=[validate_username])
    class Meta:
        model = CustomUser
        fields = ['username', 'email','password',]

    def create(self, validated_data):
        user=CustomUser.objects.create(username=validated_data['username'],email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user




class PatientSerializer(serializers.ModelSerializer):
    user = AdminSerializer()
    class Meta:
        model = Patient
        fields = ['id','user','name','dob','gender','phone_number']

    def create(self, validated_data):

        user_data=validated_data.pop('user')
        user=CustomUser.objects.create(username=user_data["username"],email=user_data['email'])
        user.set_password(user_data['password'])
        user.is_patient=True
        user.save()
        patient=Patient.objects.create(user=user, **validated_data)
        patient.save()
        return patient


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    # default_error_messages = {
    #     'no_active_account': {'Custom message': ' No active account found with the given credentials'},
    #     'blank_email': 'Custom message: Please fill in all required fields.',
    # }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # adding custom claims
        token['username'] = user.username
        token["email"] = user.email
        token['is_superuser'] = user.is_superuser
        token['is_patient'] = user.is_patient
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        if user:
            data["username"] = user.username
            data["email"] = user.email
            data["is_superuser"] = user.is_superuser
            data['is_patient'] = user.is_patient
            return data
        else:
            raise serializers.ValidationError("Only users are allowed to log in here.")


class AllHospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model=Hospital
        fields="__all__"
        

class DepartmentSerializer(serializers.ModelSerializer):
    hospital=AllHospitalSerializer()
    class Meta:
        model = Department
        fields = "__all__"

class DoctorsSerializer(serializers.ModelSerializer):
    # hospital_and_department=DepartmentSerializer()
    # image=serializers.ImageField(max_length=None,use_url=True,required=False)
    class Meta:
        model = Doctor
        fields = "__all__"
        
        
class AppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = ['id', 'day', 'time', 'time_created','user','doctor','amount']
        read_only_fields = ['user', 'time_created','doctor']
        
class AppointmentviewSerializer(serializers.ModelSerializer):
    doctor = DoctorsSerializer()
    hospital_name = serializers.SerializerMethodField() 
    class Meta:
        model = Appointment
        fields = "__all__"
    
    def get_hospital_name(self, obj):
         return obj.doctor.hospital_and_department.hospital.name if obj.doctor.hospital_and_department.hospital else None
    


class AvailableSlotsSerializer(serializers.Serializer):
    time = serializers.CharField()
    is_booked = serializers.BooleanField()
    
class AppointmentAlertSerializer(serializers.Serializer):
    message = serializers.CharField()
    