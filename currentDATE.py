import requests
import pandas as pd
from datetime import datetime
import json

# Load API key
with open("config.json") as f:
    config = json.load(f)

API_KEY = config["API_KEY"]
SYMBOL = "NVAX"
BASE_URL = "https://api.twelvedata.com/time_series"

def fetch_latest(symbol, apikey):
    """
    Fetch the most recent daily stock price (latest trading day only)
    """
    params = {
        "symbol": symbol,
        "interval": "1day",
        "apikey": apikey,
        "outputsize": 1,   # only latest available day
        "format": "JSON"
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "values" not in data:
        print("API Error:", data)
        return []

    entry = data["values"][0]
    date_str = entry["datetime"]
    close_price = entry["close"]
    formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%m/%d/%Y")

    return [{"Date": formatted_date, "Price": float(close_price)}]

# Fetch latest data
all_data = fetch_latest(SYMBOL, API_KEY)

# Convert to DataFrame
df_stock = pd.DataFrame(all_data)

# Merge into CSV
try:
    df_existing = pd.read_csv("data/nvax_history.csv")
    df_combined = pd.concat([df_existing, df_stock], ignore_index=True)
except FileNotFoundError:
    df_combined = df_stock

# Remove duplicates and sort
df_combined = df_combined.drop_duplicates(subset=["Date"]).sort_values("Date", ascending=False).reset_index(drop=True)

# Save updated CSV
df_combined.to_csv("data/nvax_history.csv", index=False)

print(f"[LOG] Added {df_stock.iloc[0]['Date']} -> {df_stock.iloc[0]['Price']}")
print("\nCSV updated. Total rows:", len(df_combined))
