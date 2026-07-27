from django.db import models
from django.utils.translation import gettext_lazy as _

class Gender(models.TextChoices):
    MALE = "male" , _("Male")
    FEMALE = "female" , _("Female")
    OTHER = "other" , _("Other")
