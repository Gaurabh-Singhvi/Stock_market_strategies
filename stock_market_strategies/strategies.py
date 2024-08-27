import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import numpy as np
import os

class StrategyAnalyzer:
    def __init__(self, stock_data):
        self.stock_data = stock_data

    def analyze(self, strategies: list) -> pd.DataFrame:
        results = []
        for symbol, data in self.stock_data.items():
            for strategy in strategies:
                if strategy == 'SMA Crossover':
                    strategy_dates = self.sma_crossover(data)
                elif strategy == 'RSI Oversold':
                    strategy_dates = self.rsi_oversold(data)
                
                for date in strategy_dates:
                    results.append({
                        'Symbol': symbol,
                        'Strategy': strategy,
                        'Date': date
                    })

        df = pd.DataFrame(results)
        
        # Ensure the output directory exists
        os.makedirs('outputs', exist_ok=True)
        
        # Save the DataFrame as a parquet file
        df.to_parquet('outputs/strategies_occurrence.parquet')
        
        return df

    def sma_crossover(self, data: pd.DataFrame) -> list:
        short_window = 50
        long_window = 200
        signals = pd.DataFrame(index=data.index)
        signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1, center=False).mean()
        signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1, center=False).mean()

        signals['signal'] = np.where(signals['short_mavg'] > signals['long_mavg'], 1, 0)
        signals['position'] = signals['signal'].diff()

        return signals[signals['position'] == 1].index.tolist()

    def rsi_oversold(self, data: pd.DataFrame) -> list:
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

        return rsi[rsi < 30].index.tolist()

# You can add more strategy methods here as needed