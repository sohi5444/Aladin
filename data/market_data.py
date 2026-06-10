import yfinance as yf

class MarketData:
    async def get_price(self, ticker: str) -> float:
        data = yf.Ticker(ticker).history(period="1d")
        return float(data['Close'].iloc[-1]) if not data.empty else 0.0
market_data = MarketData()
