

class PortfolioRow:
    def __init__(
        self,
        ticker,
        quantity=None,
        market_price=None,
        market_value=None,
        cost_basis=None,
        dollar_gain=None,
        percent_gain=None
    ):
        self.ticker = ticker
        self.quantity = quantity
        self.market_price = market_price
        self.market_value = market_value
        self.cost_basis = cost_basis
        self.dollar_gain = dollar_gain
        self.percent_gain = percent_gain

    def to_dict(self):
        """
        Convert the PortfolioRow object to a dictionary.
        """
        data = {
            "ticker": self.ticker,
            "quantity": self.quantity,
            "market_price": self.market_price,
            "market_value": self.market_value,
            "cost_basis": self.cost_basis,
            "dollar_gain": self.dollar_gain,
            "percent_gain": self.percent_gain,
        }
        return data
