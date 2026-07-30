from rest_framework import serializers
from .models import Wallet, Transaction


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = [
            "id",
            "balance",
        ]


class WalletTransactionSerializer(serializers.ModelSerializer):

    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "amount",
            "category",
            "type",
            "balance_before",
            "balance_after",
            "created_at",
        ]

    def get_created_at(self,obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")


class TransferSerializer(serializers.Serializer):
    to_wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())
    amount = serializers.IntegerField(min_value=1)

    def validate(self, data):
        sender_wallet = self.context['request'].user.wallet

        if data['to_wallet'].id == sender_wallet.id:
            raise serializers.ValidationError("Can't Transfer To Your Own Wallet")

        return data