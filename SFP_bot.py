from pybit import usdt_perpetual
import pandas as pd
import time
from time import sleep
import os

# Initialize the session and set the endpoint to the Bybit API
session_unauth = usdt_perpetual.HTTP(
    endpoint="https://api.bybit.com"
)

ws_linear = usdt_perpetual.WebSocket(
    test=True,
    ping_interval=30,  # the default is 30
    ping_timeout=10,  # the default is 10
    domain="bybit"  # the default is "bybit"
)

local_maxima = []
local_minima = []
bullish_sfp = []
bearish_sfp = []

def handle_message(msg):
    for j in range(len(local_minima)):
        if msg['data'][0]['open'] > local_minima[j] and msg['data'][0]['low'] < local_minima[j] and msg['data'][0]['close'] > local_minima[j]:
            bullish_sfp.append(msg)
            print("Bullish SFP Found!")
            print(msg)
    for j in range(len(local_maxima)):
        if msg['data'][0]['open'] < local_maxima[j] and msg['data'][0]['high'] > local_maxima[j] and msg['data'][0]['close'] < local_maxima[j]:
            bearish_sfp.append(msg)
            print("Bearish SFP Found!")
            print(msg)

# Set the start time to 1 week ago
unix_time = int(time.time()) - 7 * 24 * 60 * 60

# Initialize an empty list to store the data points
data_points = []

# Set the interval and limit for the data points
interval = 1
limit = 200

# Loop through the past week, retrieving data points for each hour
while unix_time < int(time.time()):
    # Query the Bybit API for the candlestick chart data
    response = session_unauth.query_kline(
        symbol="BTCUSDT",
        interval=interval,
        limit=limit,
        from_time=unix_time
    )
    
    # Add the data points to the list
    data_points += response['result']

    # Increment the start time by the interval
    unix_time += interval * limit * 60

# Convert the data points to a Pandas DataFrame
# df = pd.DataFrame(data_points)

# Set the number of time increments to consider for each element
time_increments = 750

# Iterate over the data array
for i in range(len(data_points)):
    # Check if the element is within the range of time increments
    if i >= time_increments and i <= len(data_points) - time_increments - 1:
        # Initialize variables to store the highest and lowest values within the range
        high = data_points[i]['high']
        low = data_points[i]['low']
        # Iterate over the data within the range
        for j in range(i - time_increments, i + time_increments + 1):
            # Update the highest and lowest values if necessary
            if data_points[j]['high'] > high:
                high = data_points[j]['high']
            if data_points[j]['low'] < low:
                low = data_points[j]['low']
        # Check if the element is a local maxima
        if data_points[i]['high'] == high:
            local_maxima.append(data_points[i]['high'])
        # Check if the element is a local minima
        if data_points[i]['low'] == low:
            local_minima.append(data_points[i]['low'])

print("maxima=")
print(local_maxima)
print("minima=")
print(local_minima)

ws_linear.kline_stream(
    handle_message, "DOTUSDT", "D"
)

while True:
    sleep(1)

# print(session_unauth.public_trading_records(
#     symbol="BTCUSDT",
#     limit=1
# ))

