from django.db import models


def greater_than_zero_constraint(field_name : str):
    return models.CheckConstraint(
            condition=models.Q(**{f"{field_name}__gt" : 0}),
            name=f"%(app_label)s_%(class)s_" + field_name + "_greater_than_zero",
        )

def should_be_unique_constraint(field_name : str):
    return models.UniqueConstraint(
        fields=[field_name],
        name=f"%(app_label)s_%(class)s_" + field_name + "_should_be_unique",
    )