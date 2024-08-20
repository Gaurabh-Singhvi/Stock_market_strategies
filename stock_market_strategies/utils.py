import pandas as pd

def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calculate percentage returns from a series of prices."""
    return prices.pct_change()

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """Calculate the Sharpe ratio of a series of returns."""
    excess_returns = returns - risk_free_rate / 252  # Assuming daily returns
    return (excess_returns.mean() * 252) / (returns.std() * (252 ** 0.5))

def calculate_drawdown(prices: pd.Series) -> pd.Series:
    """Calculate the drawdown of a series of prices."""
    return (prices - prices.cummax()) / prices.cummax()