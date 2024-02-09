import yfinance as yf
from prefect import task, flow
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB settings
INFLUXDB_URL = 'http://localhost:8086'
INFLUXDB_TOKEN = 'l2XhfWndPS6voHkJqYMs7oP8KuOv9N_R9qMIqlypuXAH7fk6YC-VCfVySF6GdwFep4PlFIdD3a1IQ-Kysvev7A=='
INFLUXDB_ORG = 'Personal'
INFLUXDB_BUCKET = 'yahoo_stocks'

@task
def log_flow_run(flow_name, run_status):
    with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = Point("flow_run").tag("flow_name", flow_name).field("status", run_status)
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

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
    log_flow_run("test prefect yahoo flow", "success")

# Run the flow
if __name__ == "__main__":
    stock_data_fetching_flow('AAPL')