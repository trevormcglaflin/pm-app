from rest_framework import serializers

from greta.models.portfolio_manager import PortfolioManager
from greta.models.transaction import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    portfolio_manager = serializers.PrimaryKeyRelatedField(queryset=PortfolioManager.objects.all())

    class Meta:
        model = Transaction
        fields = ['id', 'ticker', 'buy_action', 'num_shares', 'price_per_share', 'portfolio_manager']


class ListTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'ticker', 'buy_action', 'num_shares', 'price_per_share', 'created_date']
