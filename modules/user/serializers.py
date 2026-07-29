from rest_framework import serializers

from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):

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
        ]
        extra_kwargs = {
            "password": {"write_only": True , "read_only": False },
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data['username'] = validated_data["phone_number"]
        return User.objects.create_user(**validated_data , password = password)