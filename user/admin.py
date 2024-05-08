from django.contrib import admin

# Register your models here.
from .models import *

# admin.site.register(Patient)
# admin.site.register(CustomUser)
admin.site.register(Doctor)
admin.site.register(Hospital)
admin.site.register(Department)
# admin.site.register(Appointment)
