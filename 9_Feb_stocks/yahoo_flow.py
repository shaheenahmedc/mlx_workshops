import yfinance as yf
from prefect import task, flow
from datetime import datetime, timedelta

# Define a Prefect task to fetch stock data
@task
def fetch_stock_data(symbol: str):
    # Use yfinance to fetch the stock data
    stock = yf.Ticker(symbol)
    # Define the period for which we want the data
    # For example, the last month. You can customize this as needed.
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    # Fetch historical market data
    hist = stock.history(period="1d", interval  = "1m")
    return hist

# Define a Prefect task to process (e.g., print) the stock data
@task
def process_stock_data(hist):
    # For demonstration, we're just printing the closing prices
    hist_trimmed = hist[['Close', 'Volume']]
    hist_trimmed.to_csv('stock_data.csv')
    return hist_trimmed

# Define the Prefect flow
@flow(name = 'Stock Data Fetching Flow')
def stock_data_fetching_flow(symbol: str):
    # Fetch stock data
    hist = fetch_stock_data(symbol)
    # Process the fetched data
    process_stock_data(hist)

# Run the flow
if __name__ == "__main__":
    stock_data_fetching_flow('AAPL')
