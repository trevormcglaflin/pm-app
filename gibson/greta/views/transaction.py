import pdb

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from greta.models.portfolio_manager import PortfolioManager
from greta.models.transaction import Transaction
from greta.serializers.transaction import TransactionSerializer, ListTransactionSerializer
from greta.integrations.yahoo_finance import retrieve_latest_stock_price_from_ticker
from greta.views.portfolio_manager import get_liquid_cash_balance, get_num_shares_owned


class TransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.all()

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action in ['list', 'retrieve']:
            return ListTransactionSerializer
        else:
            return TransactionSerializer

    def list(self, request, *args, **kwargs):
        portfolio_manager_id = self.request.query_params.get('portfolio_manager_id')

        if portfolio_manager_id is not None:
            self.queryset = self.queryset.filter(portfolio_manager_id=portfolio_manager_id)

        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        transaction = request.data

        if transaction['num_shares'] <= 0:
            return Response('Number of shares must be greater than 0.', status=status.HTTP_400_BAD_REQUEST)

        portfolio_manager = PortfolioManager.objects.get(pk=transaction['portfolio_manager'])

        if not transaction['buy_action']:
            shares_owned = get_num_shares_owned(transaction['ticker'], portfolio_manager)
            if shares_owned < transaction['num_shares']:
                return Response(f'Not enough shares to sell. You own {shares_owned} shares.', status=status.HTTP_400_BAD_REQUEST)

        # grab latest stock price from yahoo finance api - rounded to two decimals
        try:
            latest_price = retrieve_latest_stock_price_from_ticker(transaction['ticker'])
            transaction['price_per_share'] = round(latest_price, 2)
        # if error occurs when retrieving stock price then return 400
        except:
            return Response('Error retrieving stock data', status=status.HTTP_400_BAD_REQUEST)

        if transaction['buy_action']:
            try:
                liquid_cash_balance = get_liquid_cash_balance(portfolio_manager)
                price_of_transaction = float(latest_price) * float(transaction['num_shares'])
                if price_of_transaction > liquid_cash_balance:
                    return Response('Not enough available cash for transaction', status=status.HTTP_400_BAD_REQUEST)
            except PortfolioManager.DoesNotExist:
                return Response('Error retrieving portfolio manager', status=status.HTTP_400_BAD_REQUEST)

        serializer = TransactionSerializer(data=transaction)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
