from django.db import models
from modules.organization.models import Organization
from modules.user.models import User


class Invoice(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="amount_gt_zero"
            )
        ]


    organization = models.ForeignKey(Organization , on_delete=models.PROTECT)
    User = models.ForeignKey(User, on_delete=models.PROTECT)
    amount = models.IntegerField(null=False , blank=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
