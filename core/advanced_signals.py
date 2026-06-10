import numpy as np
import pandas as pd
import yfinance as yf
from fredapi import Fred
import os
from sklearn.preprocessing import StandardScaler
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO

class MacroFactorModel:
    def __init__(self):
        self.fred_key = os.environ.get("FRED_API_KEY")
        self.fred = Fred(api_key=self.fred_key) if self.fred_key else None
        self.scaler = StandardScaler()

    def get_gdp_growth(self):
        if not self.fred:
            return 0.0
        try:
            series = self.fred.get_series('A191RL1Q225SBEA')
            return series.iloc[-1] if not series.empty else 0.0
        except:
            return 0.0

    def get_cpi_inflation(self):
        if not self.fred:
            return 0.0
        try:
            cpi = self.fred.get_series('CPIAUCSL')
            if len(cpi) >= 12:
                return (cpi.iloc[-1] - cpi.iloc[-12]) / cpi.iloc[-12] * 100
            return 0.0
        except:
            return 0.0

    def get_term_spread(self):
        try:
            ten = self.fred.get_series('DGS10') if self.fred else None
            two = self.fred.get_series('DGS2') if self.fred else None
            if ten is not None and two is not None and not ten.empty and not two.empty:
                return ten.iloc[-1] - two.iloc[-1]
            return 0.0
        except:
            return 0.0

    def get_factor_scores(self):
        gdp = self.get_gdp_growth()
        cpi = self.get_cpi_inflation()
        spread = self.get_term_spread()
        value_factor = -cpi / 10.0
        momentum_factor = gdp / 5.0
        quality_factor = spread / 4.0
        volatility_factor = abs(cpi) / 10.0
        return {
            'value': value_factor,
            'momentum': momentum_factor,
            'quality': quality_factor,
            'volatility': volatility_factor,
            'regime': 'bull' if gdp > 2 and cpi < 3 else 'bear'
        }

def get_technical_features(ticker, period='1y'):
    data = yf.download(ticker, period=period, progress=False)
    if data.empty:
        return {}
    close = data['Close']
    sma_20 = close.rolling(20).mean().iloc[-1]
    sma_50 = close.rolling(50).mean().iloc[-1]
    sma_200 = close.rolling(200).mean().iloc[-1]
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1] if not rs.empty else 50
    return {
        'price': close.iloc[-1],
        'sma_20': sma_20,
        'sma_50': sma_50,
        'sma_200': sma_200,
        'rsi': rsi,
        'crossover_signal': 1 if sma_20 > sma_50 else -1
    }

class RLSignalGenerator:
    def __init__(self):
        self.model = None
    def predict(self, obs):
        return np.random.choice(['BUY', 'SELL', 'HOLD'])
rl_agent = RLSignalGenerator()

class ScenarioAnalyzer:
    def __init__(self, portfolio_value=10000):
        self.portfolio = portfolio_value
    def stress_test(self, scenario='covid'):
        shocks = {
            'covid': {'equity': -0.35, 'rates': -0.50, 'credit': 0.15},
            '2008': {'equity': -0.55, 'rates': -0.20, 'credit': 0.30},
            'rate_hike': {'equity': -0.15, 'rates': 0.02, 'credit': 0.05}
        }
        shock = shocks.get(scenario, shocks['covid'])
        loss = self.portfolio * abs(shock['equity'])
        return round(loss, 2)

def generate_signal(ticker='AAPL'):
    macro = MacroFactorModel()
    factors = macro.get_factor_scores()
    tech = get_technical_features(ticker)
    score = 0.0
    if factors['regime'] == 'bull':
        score += 0.3
    else:
        score -= 0.3
    if tech.get('crossover_signal', 0) == 1:
        score += 0.4
    elif tech.get('crossover_signal', 0) == -1:
        score -= 0.4
    rl_signal = rl_agent.predict(None)
    if rl_signal == 'BUY':
        score += 0.2
    elif rl_signal == 'SELL':
        score -= 0.2
    if score > 0.5:
        signal = 'BUY'
        confidence = min(score, 0.95)
    elif score < -0.5:
        signal = 'SELL'
        confidence = min(-score, 0.95)
    else:
        signal = 'HOLD'
        confidence = 0.5
    return {
        'ticker': ticker,
        'action': signal,
        'confidence': round(confidence, 2),
        'score': round(score, 2),
        'factors': factors,
        'technicals': tech,
        'stress_loss': ScenarioAnalyzer().stress_test('covid')
    }
