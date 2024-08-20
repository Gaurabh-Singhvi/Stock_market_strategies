from src.data_reader import DataReader
from src.strategies import StrategyAnalyzer
from src.backtesting import Backtester
from src.utils import calculate_sharpe_ratio, calculate_drawdown

def run_basic_analysis():
    print("Running Basic Analysis for Stock Market Strategies")
    
    # Read data
    data_reader = DataReader('../data/stock_data')
    stock_data = data_reader.read_stock_data(['AAPL', 'GOOGL', 'MSFT'])
    
    # Analyze strategies
    analyzer = StrategyAnalyzer(stock_data)
    strategy_results = analyzer.analyze(['SMA Crossover', 'RSI Oversold'])
    
    # Run backtest
    backtester = Backtester(stock_data, strategy_results)
    backtest_results = backtester.run_backtest('2022-01-01', '2022-12-31')
    
    # Calculate additional metrics
    for symbol, data in stock_data.items():
        returns = data['Close'].pct_change()
        sharpe = calculate_sharpe_ratio(returns)
        max_drawdown = calculate_drawdown(data['Close']).min()
        
        print(f"\nAdditional metrics for {symbol}:")
        print(f"Sharpe Ratio: {sharpe:.2f}")
        print(f"Max Drawdown: {max_drawdown:.2%}")

if __name__ == "__main__":
    run_basic_analysis()