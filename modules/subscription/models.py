from django.db import models
from django.db.models import F
from django.utils import timezone

from modules.common.constraints import enum_constraint
from modules.common.constraints import positive_constraint
from modules.subscription.enums import SubscriptionStatus
from modules.user.models import User
from modules.invoice.models import Invoice
from modules.organization.models import Organization
from modules.organization.models import OrganizationSubscription


class UserSubscription(models.Model):
    class Meta:
        db_table = 'user_subscriptions'
        indexes = [
            models.Index(fields=["user_id" , "organization_id" , "status"])
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(expiration_date__gt=F("start_date")),
                name="start_date_less_than_expiration_date"
            ),
            positive_constraint(field_name="available_usage"),
            enum_constraint(field_name="status" , types = SubscriptionStatus)
        ]

    organization = models.ForeignKey(Organization , related_name="user_subscriptions", on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice , related_name="subscription" , on_delete=models.CASCADE)
    user = models.ForeignKey(User , related_name="subscriptions", on_delete=models.PROTECT)
    organization_subscription = models.ForeignKey(OrganizationSubscription , on_delete=models.PROTECT)
    status = models.CharField(choices=SubscriptionStatus , default=SubscriptionStatus.ACTIVE , max_length=13)

    available_usage = models.IntegerField(null=True , blank=True)
    last_used = models.DateTimeField(null=True, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)