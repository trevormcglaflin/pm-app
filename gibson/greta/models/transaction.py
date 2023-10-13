from django.db import models

from greta.models.portfolio_manager import PortfolioManager


class Transaction(models.Model):
    ticker = models.CharField(max_length=100)
    buy_action = models.BooleanField(blank=False, null=False)
    num_shares = models.IntegerField(blank=False, null=False)
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    portfolio_manager = models.ForeignKey(PortfolioManager, models.CASCADE)
    created_date = models.DateTimeField(auto_now=True)
