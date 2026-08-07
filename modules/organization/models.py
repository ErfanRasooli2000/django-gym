from django.db import models

from modules.common.constraints import enum_constraint
from modules.common.constraints import should_be_unique_constraint, greater_than_zero_constraint
from modules.subscription.enums import SubscriptionType

from modules.user.models import User

class Organization(models.Model):
    class Meta:
        db_table = "organizations"
        constraints = [
            models.UniqueConstraint(fields=["name"] , name="name_unique")
        ]

    name = models.CharField(null=False , blank=False , max_length=100)
    owner = models.ForeignKey(User , on_delete=models.SET_NULL , null = True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

class OrganizationSubscription(models.Model):
    class Meta:
        db_table = "organization_subscriptions"
        constraints = [
            greater_than_zero_constraint(field_name="price"),
            should_be_unique_constraint(field_name="name"),
            enum_constraint(field_name="type" , types=SubscriptionType),
        ]

    name = models.CharField(max_length=100, null=False , blank=False)
    price = models.IntegerField()
    type = models.CharField(choices = SubscriptionType ,max_length=10)
    usage_limit = models.IntegerField(null=True , blank=True)
    organization = models.ForeignKey(Organization , related_name="subscriptions" , on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)



class OrganizationProduct(models.Model):
    class Meta:
        db_table = "organization_products"
        constraints = [
            greater_than_zero_constraint(field_name="price"),
            should_be_unique_constraint(field_name="name"),
        ]

    name = models.CharField(max_length=100)
    price = models.IntegerField()
    organization = models.ForeignKey(Organization , related_name="products", on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)