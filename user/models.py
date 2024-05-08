from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin



class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)

        try:
            user.validate_unique()
        except ValidationError as e:
            raise ValidationError({'error': 'Username or email already exists.'}) from e

        user.save(using=self._db)
        return user


    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_patient = models.BooleanField('patient status',default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

class Hospital(models.Model):
    name = models.CharField(max_length=255,null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    contact_information = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='hospital_images', null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name
    
class Department(models.Model):
    department_name = models.CharField(max_length=255, )
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='department_images', null=True, blank=True)
    
    def __str__(self):
        return f"hospital: {self.hospital} | department: {self.department_name}"

class Doctor(models.Model):
   
    name = models.CharField(max_length=255,null=True, blank=True)
    specialization = models.CharField(max_length=255, null=True, blank=True)
    # hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE,)
    hospital_and_department= models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    degree = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='doctor_images', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    experience = models.PositiveIntegerField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.name} | {self.hospital_and_department}"

class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255,null=True, blank=True)
    phone_number= models.CharField(max_length=255, null=True, blank=True)
    dob = models.DateField(null=True, blank=True) 
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    gender = models.CharField(max_length=10,choices=GENDER_CHOICES, null=True, blank=True) 

    def __str__(self):
        return self.name



TIME_CHOICES = [
        ("10:00 AM", "10:00 AM"),
        ("10:30 AM", "10:30 AM"),
        ("11:00 AM", "11:00 AM"),
        ("11:30 AM", "11:30 AM"),
        ("12:00 PM", "12:00 PM"),
        ("12:30 PM", "12:30 PM"),
        ("02:00 PM", "02:00 PM"),
        ("02:30 PM", "02:30 PM"),
        ("03:00 PM", "03:00 PM"),
        ("03:30 PM", "03:30 PM"),
        ("04:00 PM", "04:00 PM"),
        ("04:30 PM", "04:30 PM"),
    ]
class Appointment(models.Model):
    user = models.ForeignKey(Patient, on_delete=models.CASCADE,)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    # hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, null=True, blank=True)
    day = models.DateField()
    time = models.CharField(max_length=10, choices=TIME_CHOICES)
    amount =models.CharField(max_length=10, default="100")
    # symptoms = models.TextField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.name} doctor: {self.doctor.name}| day: {self.day} | time: {self.time}"

