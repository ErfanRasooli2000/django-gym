from django.db import models
from django.utils.translation import gettext_lazy as _

class SubscriptionType(models.TextChoices):
    YEARLY = "Yearly" , _("Yearly")
    MONTHLY = "Monthly" , _("Monthly")
    DAILY = "Daily" , _("Daily")
    HOURLY = "Hourly" , _("Hourly")


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "Active" , _("Active")
    FINISHED = "Finished" , _("Finished")