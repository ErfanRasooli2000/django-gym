from email.policy import default

from django.db import models
from django.db.models import F
from django.utils import timezone

from modules.subscription.enums import SubscriptionType, SubscriptionStatus
from modules.user.models import User
from modules.invoice.models import Invoice
from modules.organization.models import Organization

# Create your models here.
class Subscription(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=["user_id" , "organization_id" , "status"])
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(expiration_date__gt=F("start_date")),
                name="start_date_less_than_expiration_date"
            ),
            models.CheckConstraint(
                condition=models.Q(available_usage__gte=0),
                name="available_usage_should_not_be_ngeative"
            )
        ]

    organization = models.ForeignKey(Organization , related_name="subscriptions", on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice , related_name="subscription" , on_delete=models.CASCADE)
    user = models.ForeignKey(User , related_name="subscriptions", on_delete=models.PROTECT)
    type = models.CharField(choices=SubscriptionType.choices , null=False, blank=False , max_length=10)
    status = models.CharField(choices=SubscriptionStatus.choices , default=SubscriptionStatus.ACTIVE , max_length=13)

    available_usage = models.IntegerField(null=True , blank=True)
    last_used = models.DateTimeField(null=True, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)