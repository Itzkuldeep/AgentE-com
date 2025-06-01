# filename: plot_stock_gains.py
import yfinance as yf
import matplotlib.pyplot as plt
import time

# Define stock symbols and the date range
stocks = ['TSLA', 'META']
start_date = '2025-01-01'
end_date = '2025-06-01'

ytd_gains = {}

# Attempt to fetch historical data for each stock separately
for stock in stocks:
    success = False
    for attempt in range(10):  # Increase attempts for a longer wait
        try:
            data = yf.download(stock, start=start_date, end=end_date)['Adj Close']
            if data.empty:
                raise ValueError(f"No data found for {stock}.")
            ytd_gain = ((data.iloc[-1] - data.iloc[0]) / data.iloc[0]) * 100
            ytd_gains[stock] = ytd_gain
            success = True
            break  # Break if successful
        except Exception as e:
            print(f"Attempt {attempt + 1} for {stock} failed: {e}")
            time.sleep(60)  # Wait for 60 seconds before retrying
            if attempt == 9:  # Last attempt
                print(f"Failed to download stock data for {stock} after several attempts.")
                exit()

# Plotting
plt.figure(figsize=(10, 5))
plt.bar(ytd_gains.keys(), ytd_gains.values(), color=['blue', 'green'])
plt.title('YTD Stock Price Gains for TSLA and META (2025)')
plt.xlabel('Stocks')
plt.ylabel('YTD Gain (%)')
plt.grid(axis='y')

# Save the plot to a file
plt.savefig('stock_gains.png')
plt.close()  # Close the plot to free up memory

# Output the gains to verify
print("YTD Gains (2025):")
print(ytd_gains)