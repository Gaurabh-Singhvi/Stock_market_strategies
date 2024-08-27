import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import numpy as np
from typing import Dict
import yaml
from tqdm import tqdm

class Backtester:
    def __init__(self, stock_data: Dict[str, pd.DataFrame], config_path: str, verbose: bool = False):
        self.stock_data = stock_data
        self.config = self._load_config(config_path)
        self.verbose = verbose
        self.strategy_occurrences = pd.read_parquet('outputs/strategies_occurrence.parquet')

    def _load_config(self, config_path: str) -> Dict:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)

    def run_backtest(self, start_date: str, end_date: str) -> pd.DataFrame:
        results = []
        strategies = self.strategy_occurrences['Strategy'].unique()
        for strategy in tqdm(strategies, desc="Backtesting Strategies", disable=not self.verbose):
            strategy_results = self._backtest_strategy(strategy, start_date, end_date)
            results.append(strategy_results)
        return pd.DataFrame(results)

    def _backtest_strategy(self, strategy: str, start_date: str, end_date: str) -> Dict:
        trades = []
        strategy_config = self.config[strategy]
        
        strategy_data = self.strategy_occurrences[
            (self.strategy_occurrences['Strategy'] == strategy) &
            (self.strategy_occurrences['Date'] >= start_date) &
            (self.strategy_occurrences['Date'] <= end_date)
        ]

        for _, row in tqdm(strategy_data.iterrows(), desc=f"Processing {strategy}", leave=False, disable=not self.verbose):
            symbol = row['Symbol']
            entry_date = row['Date']
            
            if symbol not in self.stock_data:
                continue

            stock_data = self.stock_data[symbol].loc[entry_date:]
            
            if self.verbose:
                print(f"Backtesting {strategy} for {symbol} from {entry_date}")

            # Calculate necessary indicators
            if strategy == 'SMA Crossover':
                stock_data['short_sma'] = stock_data['Close'].rolling(window=strategy_config['short_window']).mean()
                stock_data['long_sma'] = stock_data['Close'].rolling(window=strategy_config['long_window']).mean()
            elif strategy == 'RSI Oversold':
                delta = stock_data['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=strategy_config['window_length']).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=strategy_config['window_length']).mean()
                rs = gain / loss
                stock_data['rsi'] = 100.0 - (100.0 / (1.0 + rs))

            # Enter trade
            entry_price = stock_data['Open'].iloc[0]
            
            # Look for exit condition
            for i in range(1, len(stock_data)):
                try:
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
                        if self.verbose:
                            print(f"Exited trade for {symbol} at {exit_date} at price {exit_price}")
                        break
                except Exception as e:
                    if self.verbose:
                        print(f"Error evaluating exit condition for {symbol}: {e}")
                    break

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