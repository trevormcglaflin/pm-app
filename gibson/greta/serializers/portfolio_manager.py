from rest_framework import serializers
from greta.models.portfolio_manager import PortfolioManager


class PortfolioManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioManager
        fields = ['id', 'name']


class ListPortfolioManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioManager
        fields = ['id', 'name', 'created_date']
