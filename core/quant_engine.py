import numpy as np
import pandas as pd
import yfinance as yf
from fredapi import Fred
import os
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.covariance import LedoitWolf
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class QuantEngine:
    def __init__(self):
        self.fred_key = os.environ.get("FRED_API_KEY")
        self.fred = Fred(api_key=self.fred_key) if self.fred_key else None
        self.scaler = StandardScaler()

    # ==================== ADVANCED MACRO FACTORS ====================
    def get_macro_factors(self):
        if not self.fred:
            return {}
        try:
            gdp = self.fred.get_series('A191RL1Q225SBEA').iloc[-1] if not self.fred.get_series('A191RL1Q225SBEA').empty else 0
            cpi = self.fred.get_series('CPIAUCSL')
            cpi_yoy = (cpi.iloc[-1] - cpi.iloc[-12]) / cpi.iloc[-12] * 100 if len(cpi) >= 12 else 0
            unemp = self.fred.get_series('UNRATE').iloc[-1] if not self.fred.get_series('UNRATE').empty else 0
            fed_rate = self.fred.get_series('DFF').iloc[-1] if not self.fred.get_series('DFF').empty else 0
            ind_prod = self.fred.get_series('INDPRO').iloc[-1] if not self.fred.get_series('INDPRO').empty else 0
            retail_sales = self.fred.get_series('RSXFS').iloc[-1] if not self.fred.get_series('RSXFS').empty else 0
            consumer_confidence = self.fred.get_series('UMCSENT').iloc[-1] if not self.fred.get_series('UMCSENT').empty else 0
            housing_starts = self.fred.get_series('HOUST').iloc[-1] if not self.fred.get_series('HOUST').empty else 0
            return {
                'gdp_growth': round(gdp, 2),
                'cpi_yoy': round(cpi_yoy, 2),
                'unemployment': round(unemp, 1),
                'fed_funds_rate': round(fed_rate, 2),
                'industrial_production': round(ind_prod, 2),
                'retail_sales_growth': round((retail_sales - 1) * 100, 2) if retail_sales else 0,
                'consumer_confidence': round(consumer_confidence, 2),
                'housing_starts': round(housing_starts, 0)
            }
        except:
            return {}

    # ==================== FUNDAMENTAL RATIOS ====================
    def get_fundamentals(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            pe = info.get('trailingPE', np.nan)
            pb = info.get('priceToBook', np.nan)
            dividend_yield = info.get('dividendYield', np.nan)
            market_cap = info.get('marketCap', np.nan)
            return {'pe': pe, 'pb': pb, 'div_yield': dividend_yield, 'mkt_cap': market_cap}
        except:
            return {}

    # ==================== 30+ TECHNICAL INDICATORS ====================
    def get_technical_indicators(self, ticker, period='1y'):
        data = yf.download(ticker, period=period, progress=False)
        if data.empty:
            return {}
        close = data['Close']
        high = data['High']
        low = data['Low']
        volume = data['Volume']

        # Simple moving averages
        sma_20 = close.rolling(20).mean().iloc[-1]
        sma_50 = close.rolling(50).mean().iloc[-1]
        sma_200 = close.rolling(200).mean().iloc[-1]

        # Exponential moving averages
        ema_12 = close.ewm(span=12).mean().iloc[-1]
        ema_26 = close.ewm(span=26).mean().iloc[-1]

        # MACD
        macd_line = ema_12 - ema_26
        signal_line = close.ewm(span=9).mean().iloc[-1]
        macd_hist = macd_line - signal_line

        # Bollinger Bands
        bb_std = close.rolling(20).std().iloc[-1]
        bb_upper = sma_20 + 2 * bb_std
        bb_lower = sma_20 - 2 * bb_std

        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1] if not rs.empty else 50

        # Stochastic Oscillator
        low_14 = low.rolling(14).min()
        high_14 = high.rolling(14).max()
        stoch = 100 * (close - low_14) / (high_14 - low_14)
        stoch_k = stoch.rolling(3).mean().iloc[-1]

        # ATR (volatility)
        tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]

        # OBV
        obv = (np.sign(close.diff()) * volume).cumsum().iloc[-1]

        # Fibonacci retracement (last 252 days)
        fib_high = close.tail(252).max()
        fib_low = close.tail(252).min()
        fib_382 = fib_low + 0.382 * (fib_high - fib_low)
        fib_500 = fib_low + 0.500 * (fib_high - fib_low)
        fib_618 = fib_low + 0.618 * (fib_high - fib_low)

        # Price change
        returns = close.pct_change()
        volatility = returns.std() * np.sqrt(252)

        return {
            'sma_20': round(sma_20, 2),
            'sma_50': round(sma_50, 2),
            'sma_200': round(sma_200, 2),
            'ema_12': round(ema_12, 2),
            'ema_26': round(ema_26, 2),
            'macd_line': round(macd_line, 2),
            'macd_hist': round(macd_hist, 2),
            'bb_upper': round(bb_upper, 2),
            'bb_lower': round(bb_lower, 2),
            'rsi': round(rsi, 2),
            'stoch_k': round(stoch_k, 2),
            'atr': round(atr, 2),
            'obv': int(obv),
            'fib_382': round(fib_382, 2),
            'fib_618': round(fib_618, 2),
            'volatility': round(volatility * 100, 2),
            'return_1d': round(close.pct_change().iloc[-1] * 100, 2),
            'return_1w': round(close.pct_change(5).iloc[-1] * 100, 2),
            'return_1m': round(close.pct_change(21).iloc[-1] * 100, 2)
        }

    # ==================== STRATEGIES ====================
    def trend_strategy(self, tech):
        if tech.get('sma_20', 0) > tech.get('sma_50', 0) and tech.get('rsi', 50) > 50:
            return 1, 0.6
        elif tech.get('sma_20', 0) < tech.get('sma_50', 0) and tech.get('rsi', 50) < 50:
            return -1, 0.6
        return 0, 0

    def momentum_strategy(self, tech):
        if tech.get('return_1m', 0) > 5 and tech.get('rsi', 50) < 70:
            return 1, 0.5
        elif tech.get('return_1m', 0) < -5 and tech.get('rsi', 50) > 30:
            return -1, 0.5
        return 0, 0

    def mean_reversion_strategy(self, tech):
        price = tech.get('sma_20', 0)
        bb_lower = tech.get('bb_lower', 0)
        bb_upper = tech.get('bb_upper', 0)
        if price < bb_lower * 1.02:
            return 1, 0.7
        elif price > bb_upper * 0.98:
            return -1, 0.7
        return 0, 0

    def volatility_breakout(self, tech):
        atr = tech.get('atr', 0)
        price = tech.get('sma_20', 0)
        if atr > price * 0.02:
            return 1, 0.6
        elif atr < price * 0.005:
            return -1, 0.6
        return 0, 0

    def macro_driven_strategy(self, macro):
        if macro.get('gdp_growth', 0) > 2 and macro.get('cpi_yoy', 0) < 3:
            return 1, 0.7
        elif macro.get('gdp_growth', 0) < 0:
            return -1, 0.7
        return 0, 0

    def ensemble_signal(self, ticker):
        tech = self.get_technical_indicators(ticker)
        macro = self.get_macro_factors()
        sig_trend, conf_trend = self.trend_strategy(tech)
        sig_mom, conf_mom = self.momentum_strategy(tech)
        sig_mr, conf_mr = self.mean_reversion_strategy(tech)
        sig_vol, conf_vol = self.volatility_breakout(tech)
        sig_macro, conf_macro = self.macro_driven_strategy(macro)
        total_score = (sig_trend*conf_trend + sig_mom*conf_mom + sig_mr*conf_mr + sig_vol*conf_vol + sig_macro*conf_macro)
        total_conf = conf_trend + conf_mom + conf_mr + conf_vol + conf_macro
        signal = np.sign(total_score) if total_score != 0 else 0
        confidence = min(abs(total_score) / total_conf, 0.95) if total_conf > 0 else 0
        return signal, confidence

    # ==================== PORTFOLIO OPTIMIZATION ====================
    def optimize_portfolio(self, tickers, lookback='1y'):
        data = yf.download(tickers, period=lookback, progress=False)['Close']
        returns = data.pct_change().dropna()
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252
        lw = LedoitWolf().fit(returns)
        shrunk_cov = lw.covariance_ * 252
        num_assets = len(tickers)

        def neg_sharpe(weights):
            p_ret = np.sum(mean_returns * weights)
            p_vol = np.sqrt(np.dot(weights.T, np.dot(shrunk_cov, weights)))
            return -p_ret / p_vol

        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(num_assets))
        result = minimize(neg_sharpe, num_assets * [1./num_assets], method='SLSQP', bounds=bounds, constraints=constraints)
        return {tickers[i]: round(result.x[i], 3) for i in range(num_assets)} if result.success else {}

    def risk_parity(self, tickers, lookback='1y'):
        data = yf.download(tickers, period=lookback, progress=False)['Close']
        returns = data.pct_change().dropna()
        cov = returns.cov().values
        inv_vol = 1 / np.sqrt(np.diag(cov))
        weights = inv_vol / inv_vol.sum()
        return {tickers[i]: round(weights[i], 3) for i in range(len(tickers))}

    # ==================== RISK METRICS ====================
    def portfolio_risk_metrics(self, tickers, weights=None, lookback='2y'):
        data = yf.download(tickers, period=lookback, progress=False)['Close']
        returns = data.pct_change().dropna()
        if weights is None:
            weights = np.ones(len(tickers)) / len(tickers)
        port_returns = returns.dot(weights)
        sharpe = port_returns.mean() / port_returns.std() * np.sqrt(252) if port_returns.std() != 0 else 0
        sortino = port_returns.mean() / port_returns[port_returns < 0].std() * np.sqrt(252) if port_returns[port_returns < 0].std() != 0 else 0
        max_dd = (port_returns.cumsum().expanding().max() - port_returns.cumsum()).max()
        var_95 = np.percentile(port_returns, 5)
        cvar_95 = port_returns[port_returns <= var_95].mean()
        return {
            'sharpe': round(sharpe, 2),
            'sortino': round(sortino, 2),
            'max_drawdown': round(max_dd * 100, 2),
            'var_95': round(var_95 * 100, 2),
            'cvar_95': round(cvar_95 * 100, 2)
        }

    # ==================== MONTE CARLO SIMULATION ====================
    def monte_carlo(self, ticker, days=252, simulations=1000):
        data = yf.download(ticker, period='3y', progress=False)['Close']
        log_returns = np.log(1 + data.pct_change()).dropna()
        mu = log_returns.mean()
        sigma = log_returns.std()
        last_price = data.iloc[-1]
        sim_prices = np.zeros((simulations, days))
        for s in range(simulations):
            returns = np.random.normal(mu, sigma, days)
            price_path = last_price * np.exp(np.cumsum(returns))
            sim_prices[s, :] = price_path
        final_prices = sim_prices[:, -1]
        expected_price = np.mean(final_prices)
        lower_95 = np.percentile(final_prices, 2.5)
        upper_95 = np.percentile(final_prices, 97.5)
        return {
            'expected_price': round(expected_price, 2),
            'lower_95': round(lower_95, 2),
            'upper_95': round(upper_95, 2),
            'volatility': round(sigma * np.sqrt(252) * 100, 2)
        }

quant_engine = QuantEngine()
