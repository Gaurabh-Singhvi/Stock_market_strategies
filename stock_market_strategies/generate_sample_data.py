import pandas as pd
import numpy as np

def generate_stock_data(symbol, start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    data = pd.DataFrame({
        'Date': date_range,
        'Open': np.random.randint(100, 200, size=len(date_range)),
        'High': np.random.randint(150, 250, size=len(date_range)),
        'Low': np.random.randint(50, 150, size=len(date_range)),
        'Close': np.random.randint(100, 200, size=len(date_range)),
        'Volume': np.random.randint(1000000, 5000000, size=len(date_range))
    })
    data.set_index('Date', inplace=True)
    data.to_csv(f'data/{symbol}.csv')

# Generate data for three stocks
for symbol in ['AAPL', 'GOOGL', 'MSFT']:
    generate_stock_data(symbol, '2022-01-01', '2022-12-31')

print("Sample data generated.")