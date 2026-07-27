from django.contrib.auth.models import AbstractUser
from django.db import models
from .enums import Gender
from .validators import iranian_mobile_validator


# Create your models here.
class User(AbstractUser):
    REQUIRED_FIELDS = ["phone_number" , "email"]

    phone_number = models.CharField(max_length=11, unique=True , validators=[iranian_mobile_validator])
    gender = models.CharField(choices=Gender.choices, max_length=10, blank=True)
    birth_date = models.DateField(null=True, blank=True)


    def __str__(self):
        return self.phone_number