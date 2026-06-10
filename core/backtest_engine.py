import pandas as pd
from backtesting import Backtest, Strategy
from core.real_prices import get_historical_stock

class SmaCross(Strategy):
    n1 = 50
    n2 = 200

    def init(self):
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), self.data.Close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), self.data.Close)

    def next(self):
        if self.sma1[-1] > self.sma2[-1] and self.sma1[-2] <= self.sma2[-2]:
            self.buy()
        elif self.sma1[-1] < self.sma2[-1] and self.sma1[-2] >= self.sma2[-2]:
            self.sell()

def run_backtest(ticker, start_date, end_date, cash=10000):
    data = get_historical_stock(ticker)
    if data.empty:
        return None
    data = data.loc[start_date:end_date]
    bt = Backtest(data, SmaCross, cash=cash, commission=.001)
    result = bt.run()
    return {
        'start': start_date,
        'end': end_date,
        'return_pct': result['Return [%]'],
        'max_dd_pct': result['Max Drawdown [%]'],
        'sharpe': result['Sharpe Ratio'],
        'trades': result['# Trades'],
        'win_rate': result['Win Rate [%]']
    }
