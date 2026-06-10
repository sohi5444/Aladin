import pandas as pd
import numpy as np
import yfinance as yf
from core.quant_engine import quant_engine

def walk_forward_backtest(ticker, start_date, end_date, window_years=1, step_years=0.25):
    data = yf.download(ticker, period='5y', progress=False)['Close']
    dates = pd.date_range(start_date, end_date, freq=step_years)
    trades = []
    for i in range(len(dates)-1):
        train_start = dates[i] - pd.DateOffset(years=window_years)
        train_end = dates[i]
        test_start = dates[i]
        test_end = dates[i+1]
        if train_start < data.index[0]:
            continue
        # Train ensemble weights (simplified: use historical volatility)
        tech = quant_engine.get_technical_indicators(ticker)
        signal, conf = quant_engine.ensemble_signal(ticker)
        # Simulate trade on test period
        test_data = data.loc[test_start:test_end]
        if len(test_data) < 2:
            continue
        ret = test_data.pct_change().mean() * 252  # annualized
        if signal == 1:
            pnl = ret * 0.01  # assume 1% risk per trade
            trades.append(pnl)
        elif signal == -1:
            pnl = -ret * 0.01
            trades.append(pnl)
    if not trades:
        return None
    pnl_series = pd.Series(trades)
    total_return = pnl_series.sum() * 100
    sharpe = pnl_series.mean() / pnl_series.std() * np.sqrt(252) if pnl_series.std() != 0 else 0
    max_dd = (pnl_series.cumsum().expanding().max() - pnl_series.cumsum()).max() * 100
    win_rate = (pnl_series > 0).mean() * 100
    return {
        'total_return_pct': round(total_return, 2),
        'sharpe': round(sharpe, 2),
        'max_dd_pct': round(max_dd, 2),
        'win_rate_pct': round(win_rate, 2),
        'num_trades': len(trades)
    }
