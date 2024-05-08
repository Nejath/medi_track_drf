from django.core.exceptions import ValidationError
from .models import CustomUser
from django.core.exceptions import ObjectDoesNotExist
def validate_password_complexity(password):
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not any(char.isupper() for char in password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not any(char in "!@#$%^&*()" for char in password):
        raise ValidationError("Password must contain at least one special character (!@#$%^&*()).")


def validate_email(email):
    try:
        CustomUser.objects.get(email=email)
        raise ValidationError('Email already exists.')
    except ObjectDoesNotExist:
        pass

def validate_username(username):
    try:
        CustomUser.objects.get(username=username)
        raise ValidationError('Username already exists.')
    except ObjectDoesNotExist:
        pass