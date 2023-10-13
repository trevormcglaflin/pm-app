import yfinance as yf


def retrieve_latest_stock_price_from_ticker(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d")
    last_price = hist['Close'][0]
    return last_price
