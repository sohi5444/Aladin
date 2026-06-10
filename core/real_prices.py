import yfinance as yf
import os
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.foreignexchange import ForeignExchange

AV_KEY = os.environ.get("ALPHA_VANTAGE_KEY")

def get_stock_price(ticker):
    try:
        data = yf.download(ticker, period='1d', interval='1m', progress=False)
        if not data.empty:
            return round(float(data['Close'].iloc[-1]), 2)
    except:
        pass
    return None

def get_forex_rate(from_curr, to_curr='USD'):
    if not AV_KEY:
        return None
    try:
        fx = ForeignExchange(key=AV_KEY, output_format='pandas')
        data, _ = fx.get_currency_exchange_rate(from_currency=from_curr, to_currency=to_curr)
        return float(data['5. Exchange Rate'])
    except:
        return None

def get_historical_stock(ticker, period='2y'):
    return yf.download(ticker, period=period, progress=False)
