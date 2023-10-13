from django.db import models


class PortfolioManager(models.Model):
    name = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True)
    cash_basis = models.DecimalField(max_digits=10, decimal_places=2, default=0)
