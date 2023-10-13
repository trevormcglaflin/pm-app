import pdb
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar


from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from greta.classes.portfolio_row import PortfolioRow
from greta.models.portfolio_manager import PortfolioManager
from greta.models.transaction import Transaction
from greta.serializers.portfolio_manager import PortfolioManagerSerializer, ListPortfolioManagerSerializer
from greta.integrations.yahoo_finance import retrieve_latest_stock_price_from_ticker


class PortfolioManagerViewSet(ModelViewSet):
    queryset = PortfolioManager.objects.all()

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action in ['list', 'retrieve']:
            return ListPortfolioManagerSerializer
        else:
            return PortfolioManagerSerializer

    @action(detail=True, methods=['GET'])
    def get_portfolio(self, request, pk=None):
        """
        Custom action that requires a detail view.
        """
        instance = self.get_object()  # Get the object for the detail view
        portfolio_rows = get_portfolio_rows(instance)
        return Response([portfolio_row.to_dict() for portfolio_row in portfolio_rows])

    @action(detail=True, methods=['GET'])
    def get_ttm_portfolio_chart_data(self, request, pk=None):
        """
        Custom action that requires a detail view.
        chartData = [
            {
              name: 'AAPL',
              series: [
                { name: '12/31/2021', value: 10 },
                { name: '12/31/2022', value: 15 },
                { name: '12/31/2023', value: 22 },
              ],
            },
            {
              name: 'TSLA',
              series: [
                { name: '12/31/2021', value: 5 },
                { name: '12/31/2022', value: 7 },
                { name: '12/31/2023', value: 18 },
              ],
            },
          ];
        """
        instance = self.get_object()  # Get the object for the detail view

        date_list = get_date_list_for_last_12_months()

        series = []
        for index, date in enumerate(date_list):
            series.append({'name': date.strftime('%Y-%m-%d'), 'value': index})

        #pdb.set_trace()


        #portfolio_rows = get_portfolio_rows(instance)
        return Response(series)


    @action(detail=True, methods=['POST'])
    def update_cash_basis(self, request, pk=None):
        """
        Custom action that updates cash basis. It adds/subtracts the cash basis in payload with existing one
        """
        cash_to_add = request.data.get('cash_to_add')
        if not cash_to_add:
            Response(status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()  # Get the object for the detail view


        # get liquid cash balance
        liquid_cash_balance = get_liquid_cash_balance(instance)
        if float(liquid_cash_balance) + float(cash_to_add) < 0:
            return Response('Not enough liquid cash to withdrawal.', status=status.HTTP_400_BAD_REQUEST)

        instance.cash_basis = float(instance.cash_basis) + float(cash_to_add)
        instance.save()
        return Response({'cash_basis': instance.cash_basis}, status=status.HTTP_200_OK)


def get_portfolio_rows(portfolio_manager):
    transactions = Transaction.objects.filter(portfolio_manager_id=portfolio_manager.id)
    portfolio_rows = []
    ticker_map = {}
    for transaction in transactions:
        if transaction.ticker not in ticker_map:
            portfolio_rows.append(PortfolioRow(ticker=transaction.ticker))
            ticker_map[transaction.ticker] = 1

    for portfolio_row in portfolio_rows:
        quantity, cost_basis = get_portfolio_row_data_for_ticker_from_transactions(portfolio_row.ticker, transactions)
        portfolio_row.quantity = quantity
        portfolio_row.cost_basis = cost_basis
        market_price = retrieve_latest_stock_price_from_ticker(portfolio_row.ticker)
        portfolio_row.market_value = round(market_price * portfolio_row.quantity, 2)
        portfolio_row.dollar_gain = round(portfolio_row.market_value - float(portfolio_row.cost_basis), 2)
        portfolio_row.percent_gain = round(portfolio_row.dollar_gain / float(portfolio_row.cost_basis), 4)
        portfolio_row.market_price = round(market_price, 2)
    total_row = get_total_portfolio_row(portfolio_rows)
    portfolio_rows.append(total_row)
    liquid_cash_row = get_liquid_cash_row(total_row.cost_basis, portfolio_manager.cash_basis)
    portfolio_rows.append(liquid_cash_row)
    portfolio_rows.append(get_total_row_including_cash(total_row, liquid_cash_row, portfolio_manager.cash_basis))
    return portfolio_rows


def get_portfolio_row_data_for_ticker_from_transactions(ticker, transactions):
    quantity = 0
    total_cost = 0
    for transaction in transactions:
        if transaction.ticker == ticker:
            if transaction.buy_action:
                quantity += transaction.num_shares
                total_cost += transaction.num_shares * transaction.price_per_share

            else:
                quantity -= transaction.num_shares
                total_cost -= transaction.num_shares * transaction.price_per_share

    return quantity, total_cost


def get_total_portfolio_row(portfolio_rows):
    total_row = PortfolioRow(ticker='Total Equities')
    market_value_sum = 0
    cost_basis_sum = 0
    for portfolio_row in portfolio_rows:
        market_value_sum += portfolio_row.market_value
        cost_basis_sum += portfolio_row.cost_basis
    total_row.cost_basis = cost_basis_sum
    total_row.market_value = market_value_sum
    total_row.dollar_gain = round(float(market_value_sum) - float(cost_basis_sum), 2)
    if cost_basis_sum == 0:
        total_row.percent_gain = 0
    else:
        total_row.percent_gain = round(float(total_row.dollar_gain) / float(cost_basis_sum), 4)
    return total_row


def get_liquid_cash_row(cost_basis, cash_basis):
    cash_row = PortfolioRow(ticker="Available Cash")
    available_cash = float(cash_basis) - float(cost_basis)
    cash_row.market_value = available_cash
    cash_row.cost_basis = available_cash
    return cash_row


def get_total_row_including_cash(total_row_before_cash, liquid_cash_row, cash_basis):
    total_row = PortfolioRow("Total")
    total_row.cost_basis = cash_basis
    total_row.market_value = float(total_row_before_cash.market_value) + float(liquid_cash_row.market_value)
    total_row.dollar_gain = round(float(total_row.market_value) - float(total_row.cost_basis), 2)
    if total_row.cost_basis == 0:
        total_row.percent_gain = 0
    else:
        total_row.percent_gain = round(float(total_row.dollar_gain) / float(total_row.cost_basis), 4)
    return total_row


def get_liquid_cash_balance(portfolio_manager):
    portfolio_rows = get_portfolio_rows(portfolio_manager)
    # not the most robust here
    return portfolio_rows[-2].market_value


def get_num_shares_owned(ticker, portfolio_manager):
    transactions = Transaction.objects.filter(portfolio_manager_id=portfolio_manager.id)
    num_shares_owned = 0
    for transaction in transactions:
        if transaction.ticker == ticker:
            if transaction.buy_action:
                num_shares_owned += transaction.num_shares
            else:
                num_shares_owned -= transaction.num_shares
    return num_shares_owned


def get_date_list_for_last_12_months():
    current_date = datetime.now()
    date_list = []
    for i in range(12):
        day = min(current_date.day, calendar.monthrange(current_date.year, current_date.month)[1])
        new_date = datetime(current_date.year, current_date.month, day)
        date_list.append(new_date)
        if current_date.month == 1:
            current_date = datetime(current_date.year - 1, 12, day)
        else:
            current_date = datetime(current_date.year, current_date.month - 1, day)
    return date_list
