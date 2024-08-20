import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import numpy as np
from typing import Dict
import yaml
from tqdm import tqdm

class Backtester:
    def __init__(self, stock_data: Dict[str, pd.DataFrame], strategy_results: pd.DataFrame, config_path: str, verbose: bool = False):
        self.stock_data = stock_data
        self.strategy_results = strategy_results
        self.config = self._load_config(config_path)
        self.verbose = verbose

    def _load_config(self, config_path: str) -> Dict:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)

    def run_backtest(self, start_date: str, end_date: str) -> pd.DataFrame:
        results = []
        strategies = self.strategy_results.columns[1:]  # Skip 'Symbol' column
        for strategy in tqdm(strategies, desc="Backtesting Strategies", disable=not self.verbose):
            strategy_results = self._backtest_strategy(strategy, start_date, end_date)
            results.append(strategy_results)
        return pd.DataFrame(results)

    def _backtest_strategy(self, strategy: str, start_date: str, end_date: str) -> Dict:
        trades = []
        strategy_config = self.config[strategy]
        symbols = self.strategy_results[self.strategy_results[strategy] == 1]['Symbol']

        for symbol in tqdm(symbols, desc=f"Processing {strategy}", leave=False, disable=not self.verbose):
            stock_data = self.stock_data[symbol].loc[start_date:end_date]
            
            if self.verbose:
                print(f"Backtesting {strategy} for {symbol}")
                print(f"Data points: {len(stock_data)}")

            # Calculate indicators
            if strategy == 'SMA Crossover':
                stock_data['short_sma'] = stock_data['Close'].rolling(window=strategy_config['short_window']).mean()
                stock_data['long_sma'] = stock_data['Close'].rolling(window=strategy_config['long_window']).mean()
            elif strategy == 'RSI Oversold':
                delta = stock_data['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=strategy_config['window_length']).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=strategy_config['window_length']).mean()
                rs = gain / loss
                stock_data['rsi'] = 100 - (100 / (1 + rs))

            in_position = False
            for i in range(1, len(stock_data)):
                if not in_position:
                    # Entry condition
                    entry_condition = eval(strategy_config['entry_condition'], globals(), stock_data.iloc[i].to_dict())
                    if entry_condition:
                        entry_price = stock_data['Open'].iloc[i]
                        entry_date = stock_data.index[i]
                        in_position = True
                        if self.verbose:
                            print(f"Entered trade for {symbol} at {entry_date} at price {entry_price}")
                
                elif in_position:
                    # Exit condition
                    exit_condition = eval(strategy_config['exit_condition'], globals(), stock_data.iloc[i].to_dict())
                    if exit_condition:
                        exit_price = stock_data['Open'].iloc[i]
                        exit_date = stock_data.index[i]
                        trades.append({
                            'symbol': symbol,
                            'entry_date': entry_date,
                            'exit_date': exit_date,
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                        })
                        in_position = False
                        if self.verbose:
                            print(f"Exited trade for {symbol} at {exit_date} at price {exit_price}")

        trades_df = pd.DataFrame(trades)
        if self.verbose:
            print(f"Total trades for {strategy}: {len(trades_df)}")

        if not trades_df.empty:
            trades_df['return'] = (trades_df['exit_price'] - trades_df['entry_price']) / trades_df['entry_price']
            abs_return = trades_df['return'].sum()
            hit_ratio = (trades_df['return'] > 0).mean()
            avg_gain = trades_df[trades_df['return'] > 0]['return'].mean() if len(trades_df[trades_df['return'] > 0]) > 0 else 0
            avg_loss = trades_df[trades_df['return'] < 0]['return'].mean() if len(trades_df[trades_df['return'] < 0]) > 0 else 0
        else:
            abs_return = hit_ratio = avg_gain = avg_loss = 0

        return {
            'Strategy_name': strategy,
            'Abs Return': abs_return,
            'Hit Ratio': hit_ratio,
            'Average Gain': avg_gain,
            'Average Loss': avg_loss
        }