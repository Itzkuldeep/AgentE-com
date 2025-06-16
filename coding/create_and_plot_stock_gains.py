# filename: create_and_plot_stock_gains.py
import pandas as pd
import matplotlib.pyplot as plt

# Create a sample CSV file with stock data
data = {
    'Date': pd.date_range(start='2025-01-01', end='2025-06-01', freq='D'),
    'TSLA': [700 + i * 1.3 for i in range(152)],  # Simulate prices incrementing for TSLA
    'META': [325 + i * 0.5 for i in range(152)]   # Simulate prices incrementing for META
}

# Convert to DataFrame and save to CSV
df = pd.DataFrame(data)
df.to_csv('stock_data.csv', index=False)
print("CSV file 'stock_data.csv' created.")

# Load data from the CSV file
data_loaded = pd.read_csv('stock_data.csv', parse_dates=['Date'], index_col='Date')

# Calculate YTD gains for each stock
ytd_gains = ((data_loaded.iloc[-1] - data_loaded.iloc[0]) / data_loaded.iloc[0]) * 100

# Plotting
plt.figure(figsize=(10, 5))
plt.bar(ytd_gains.index, ytd_gains.values, color=['blue', 'green'])
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