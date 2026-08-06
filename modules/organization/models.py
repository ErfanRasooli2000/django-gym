from django.db import models
from modules.user.models import User

class Organization(models.Model):
    name = models.CharField(null=False , blank=False , max_length=100)
    owner = models.ForeignKey(User , on_delete=models.SET_NULL , null = True)