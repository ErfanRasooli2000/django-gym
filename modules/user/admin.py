from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Gym profile", {"fields": ("phone_number", "gender", "birth_date", "wallet")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Gym profile", {"fields": ("phone_number", "gender", "birth_date")}),
    )
    list_display = ("username", "phone_number", "email", "is_staff")
