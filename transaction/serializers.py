from rest_framework import serializers

from transaction.models import Transaction


class TransactionListSerializer(serializers.ModelSerializer):
    transaction_number = serializers.CharField(source='txn_no')
    transaction_type = serializers.CharField(source='type')

    class Meta:
        model = Transaction
        fields = ('transaction_number', 'transaction_type', 'amount')
