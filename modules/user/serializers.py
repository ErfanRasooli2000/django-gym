from .services import register_user
from rest_framework import serializers
from modules.wallet.serializers import WalletSerializer
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):

    wallet = WalletSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "email",
            "gender",
            "birth_date",
            "wallet",
        ]

        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        return register_user(validated_data , password=password)