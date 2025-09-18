import requests
import pandas as pd
from datetime import datetime
import time

API_KEY = "e90ef301070141d4af8ba1f15f26989b"
SYMBOL = "NVAX"

# Twelve Data time_series endpoint (daily data)
BASE_URL = "https://api.twelvedata.com/time_series"

# Function to pull daily historical data
def fetch_historical(symbol, apikey, start_date=None):
    params = {
        "symbol": symbol,
        "interval": "1day",
        "apikey": apikey,
        "outputsize": 5000,   # max available in one call
        "format": "JSON"
    }
    if start_date:
        params["start_date"] = start_date

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "values" not in data:
        print("API Error:", data)
        return []

    return data["values"]

# Main loop
all_data = []
used_calls = 0

# First fetch
values = fetch_historical(SYMBOL, API_KEY)
used_calls += 1

if values:
    for entry in values:
        date_str = entry["datetime"]
        close_price = entry["close"]

        # Convert to mm/dd/yyyy
        formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%m/%d/%Y")

        all_data.append({"Date": formatted_date, "Price": float(close_price)})
        print(f"[LOG] Added {formatted_date} -> {close_price}")

# Turn into DataFrame
df = pd.DataFrame(all_data)

# Sort newest first
df = df.sort_values("Date", ascending=False).reset_index(drop=True)

print("\nFinal DataFrame:")
print(df)

# Save if you want
df.to_csv("nvax_history2.csv", index=False)
