import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import numpy as np
from typing import Dict

def sma_crossover(data: pd.DataFrame, short_window: int = 50, long_window: int = 200) -> bool:
    short_sma = data['Close'].rolling(window=short_window).mean()
    long_sma = data['Close'].rolling(window=long_window).mean()
    return short_sma.iloc[-1] > long_sma.iloc[-1]

def rsi_oversold(data: pd.DataFrame, window: int = 14, threshold: int = 30) -> bool:
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] < threshold

class StrategyAnalyzer:
    def __init__(self, stock_data):
        self.stock_data = stock_data

    def analyze(self, strategies: list) -> pd.DataFrame:
        results = []
        for symbol, data in self.stock_data.items():
            row = {'Symbol': symbol}
            for strategy in strategies:
                if strategy == 'SMA Crossover':
                    row[strategy] = int(self.sma_crossover(data))
                elif strategy == 'RSI Oversold':
                    row[strategy] = int(self.rsi_oversold(data))
            results.append(row)
        return pd.DataFrame(results)

    def sma_crossover(self, data: pd.DataFrame) -> bool:
        # Calculate short-term and long-term SMAs
        short_window = 50
        long_window = 200
        signals = pd.DataFrame(index=data.index)
        signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1, center=False).mean()
        signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1, center=False).mean()

        # Create signals
        signals['signal'] = 0.0
        signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:]
                                                    > signals['long_mavg'][short_window:], 1.0, 0.0)

        # Generate trading orders
        signals['positions'] = signals['signal'].diff()

        # Check if there's a buying opportunity (1.0) in the last 30 days
        return 1.0 in signals['positions'][-30:].values

    def rsi_oversold(self, data: pd.DataFrame) -> bool:
        # Calculate RSI
        window_length = 14
        close = data['Close']
        delta = close.diff()
        delta = delta[1:]
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        roll_up = up.rolling(window_length).mean()
        roll_down = down.abs().rolling(window_length).mean()
        rs = roll_up / roll_down
        rsi = 100.0 - (100.0 / (1.0 + rs))

        # Check if RSI is oversold (below 30) in the last 30 days
        return any(rsi[-30:] < 30)

# You can add more strategy methods here as needed