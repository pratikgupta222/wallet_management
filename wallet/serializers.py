from rest_framework import serializers

from wallet.models import Wallet


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = '__all__'
