import yfinance as yf

def calculate_daily_spread(ticker: str) -> float:
    """Calculates the daily price spread percentage of a given stock ticker."""
    stock = yf.Ticker(ticker)
    today_data = stock.history(period="1d")
    if not today_data.empty:
        high = today_data["High"].iloc[0]
        low = today_data["Low"].iloc[0]
        spread = ((high - low) / low) * 100
        return spread
    else:
        return 0  # or handle the empty case differently
