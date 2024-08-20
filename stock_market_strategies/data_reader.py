import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import os
from typing import Dict, List

class DataReader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.file_path = os.path.join(data_dir, "stock_data_raw.csv.gz")

    def read_stock_data(self, symbols: List[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Read stock data for specified symbols from the compressed CSV file.
        If no symbols are specified, return data for all available symbols.

        Args:
            symbols (List[str], optional): List of stock symbols to fetch data for.

        Returns:
            Dict[str, pd.DataFrame]: Dictionary with stock symbols as keys and corresponding DataFrames as values.
        """
        # Read the entire CSV file
        df = pd.read_csv(self.file_path, compression='gzip', parse_dates=['Date']).rename({"Stock Name": "Symbol"}, axis = 1)

        # If no specific symbols are requested, get unique symbols from the data
        if symbols is None:
            symbols = df['Symbol'].unique().tolist()

        stock_data = {}
        for symbol in symbols:
            symbol_data = df[df['Symbol'] == symbol].copy()
            if not symbol_data.empty:
                symbol_data.set_index('Date', inplace=True)
                symbol_data.sort_index(inplace=True)
                stock_data[symbol] = symbol_data
            else:
                print(f"No data found for symbol: {symbol}")

        return stock_data

    def get_available_symbols(self) -> List[str]:
        """
        Get a list of all available stock symbols in the dataset.

        Returns:
            List[str]: List of all unique stock symbols.
        """
        df = pd.read_csv(self.file_path, compression='gzip', usecols=['Symbol'])
        return df['Symbol'].unique().tolist()

# Usage example
if __name__ == "__main__":
    reader = DataReader("stock_market_strategies/data")
    
    # Get all available symbols
    all_symbols = reader.get_available_symbols()
    print(f"Available symbols: {all_symbols[:5]}... (total: {len(all_symbols)})")

    # Read data for specific symbols
    stock_data = reader.read_stock_data(['reliance.NS', 'tcs.NS', 'icicibank.NS'])
    
    for symbol, data in stock_data.items():
        print(f"\nData for {symbol}:")
        print(data.head())
        print(f"Shape: {data.shape}")