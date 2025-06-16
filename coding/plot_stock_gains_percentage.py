# filename: plot_stock_gains_percentage.py
import pandas as pd
import matplotlib.pyplot as plt

# Load data from the CSV file
data_loaded = pd.read_csv('stock_data.csv', parse_dates=['Date'], index_col='Date')

# Calculate YTD gains for each stock
ytd_gains = ((data_loaded.iloc[-1] - data_loaded.iloc[0]) / data_loaded.iloc[0]) * 100

# Plotting the percentage gains
plt.figure(figsize=(10, 5))
bars = plt.bar(ytd_gains.index, ytd_gains.values, color=['blue', 'green'])

# Adding percentage labels to bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}%', va='bottom')  # va: vertical alignment

plt.title('YTD Stock Price Gains for TSLA and META (2025) in Percentage')
plt.xlabel('Stocks')
plt.ylabel('YTD Gain (%)')
plt.ylim(0, max(ytd_gains.values) + 10)  # Set y-limit to make room for labels
plt.grid(axis='y')

# Save the plot to a file
plt.savefig('stock_gains_percentage.png')
plt.close()

# Output the gains to verify
print("YTD Gains (2025):")
print(ytd_gains)