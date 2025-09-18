import requests
import pandas as pd
from datetime import datetime, timedelta
import json

with open("config.json") as f:
    config = json.load(f)

API_KEY = config["API_KEY"]
SYMBOL = "NVAX"
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

# Fetch data
all_data = []
values = fetch_historical(SYMBOL, API_KEY)

if values:
    for entry in values:
        date_str = entry["datetime"]
        close_price = entry["close"]
        formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%m/%d/%Y")
        all_data.append({"Date": formatted_date, "Price": float(close_price)})
        print(f"[LOG] Added {formatted_date} -> {close_price}")

# Convert to DataFrame
df_stock = pd.DataFrame(all_data)

# Convert Date to datetime for proper range
df_stock["Date_dt"] = pd.to_datetime(df_stock["Date"], format="%m/%d/%Y")

# Create full daily date range from earliest to latest
start_date = df_stock["Date_dt"].min()
end_date = df_stock["Date_dt"].max()
all_dates = pd.date_range(start=start_date, end=end_date, freq="D")

# Create DataFrame with all dates
df_all_dates = pd.DataFrame({"Date_dt": all_dates})

# Merge stock prices onto full date range
df_final = pd.merge(df_all_dates, df_stock[["Date_dt", "Price"]], on="Date_dt", how="left")

# Format Date column
df_final["Date"] = df_final["Date_dt"].dt.strftime("%m/%d/%Y")
df_final = df_final[["Date", "Price"]]

# Sort newest first
df_final = df_final.sort_values("Date", ascending=False).reset_index(drop=True)

print("\nFinal DataFrame:")
print(df_final)

# Save to CSV
df_final.to_csv("nvax_history2.csv", index=False)
