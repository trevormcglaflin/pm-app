from rest_framework.routers import DefaultRouter
from greta.views.portfolio_manager import PortfolioManagerViewSet
from greta.views.transaction import TransactionViewSet
from django.urls import path
from django.conf.urls import include


router = DefaultRouter()
router.register('portfolio-manager', PortfolioManagerViewSet)
router.register('transaction', TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

