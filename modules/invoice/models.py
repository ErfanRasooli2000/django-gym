from django.db import models

from modules.common.constraints import greater_than_zero_constraint
from modules.organization.models import Organization, OrganizationProduct , OrganizationSubscription
from modules.user.models import User

class Invoice(models.Model):

    class Meta:
        db_table = 'invoices'
        constraints = [
            greater_than_zero_constraint(field_name="amount")
        ]


    organization = models.ForeignKey(Organization , on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT , related_name="invoices")
    amount = models.IntegerField(null=False , blank=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class InvoiceProducts(models.Model):

    class Meta:
        db_table = 'invoice_products'
        constraints = [
            greater_than_zero_constraint(field_name="price"),
            greater_than_zero_constraint(field_name="count"),
        ]

    product = models.ForeignKey(OrganizationProduct , on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice , on_delete=models.CASCADE)
    count = models.SmallIntegerField(default=1 , null=False, blank=False)
    price = models.IntegerField(default=0 , null=False , blank=False)


class InvoiceSubscription(models.Model):

    class Meta:
        db_table = 'invoice_subscription'
        constraints = [
            greater_than_zero_constraint(field_name="price")
        ]

    subscription = models.ForeignKey(OrganizationSubscription , on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice , on_delete=models.CASCADE)
    price = models.IntegerField(default=0 , null=False , blank=False)