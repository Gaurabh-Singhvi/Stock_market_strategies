from data_reader import DataReader
from strategies import StrategyAnalyzer
from backtesting import Backtester
import argparse

def main(verbose=False, show_progress=False):
    print("Welcome to Stock Market Strategies")
    
    # Step 1: Read data
    data_reader = DataReader('stock_market_strategies/data')
    stock_data = data_reader.read_stock_data() #['AAPL', 'GOOGL', 'MSFT']
    print("Data loaded successfully.")

    # Step 2: Analyze strategies
    analyzer = StrategyAnalyzer(stock_data)
    strategy_results = analyzer.analyze(['SMA Crossover', 'RSI Oversold'])
    print("\nStrategy Analysis Results:")
    print(strategy_results)

    # Step 3: Run backtest
    backtester = Backtester(stock_data, strategy_results, 'config/strategy_config.yaml', verbose=verbose or show_progress)
    backtest_results = backtester.run_backtest('2022-01-01', '2022-12-31')
    print("\nBacktest Results:")
    print(backtest_results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stock Market Strategies Backtester")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-p", "--progress", action="store_true", help="Show progress bar")
    args = parser.parse_args()

    main(verbose=args.verbose, show_progress=args.progress)