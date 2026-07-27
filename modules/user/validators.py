from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

iranian_mobile_validator = RegexValidator(
    regex=r"^09\d{9}$",
    message=_("Phone number must be 11 digits starting with 09."),
    code="invalid_phone",
)