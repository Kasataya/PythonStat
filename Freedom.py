import requests
import pandas as pd
from datetime import date, datetime, timedelta
import json

with open("config.json") as f:
    config = json.load(f)

API_KEY = config["API_KEY"]

SYMBOL = "NVAX"
BASE_URL = "https://api.twelvedata.com/time_series"

# Desired date range
START_DATE = "1995-01-01"
END_DATE = date.today().strftime("%Y-%m-%d")

# Function to pull daily historical data
def fetch_historical(symbol, apikey, start_date=None, end_date=None):
    params = {
        "symbol": symbol,
        "interval": "1day",
        "apikey": apikey,
        "outputsize": 5000,   # max available in one call
        "format": "JSON"
    }
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "values" not in data:
        print("API Error:", data)
        return []

    return data["values"]

# Fetch data
all_data = []
values = fetch_historical(SYMBOL, API_KEY, start_date=START_DATE, end_date=END_DATE)

if values:
    for entry in values:
        date_str = entry["datetime"]
        volume = entry.get("volume", None)  # fetch volume
        formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%m/%d/%Y")
        if volume is not None:
            all_data.append({"Date": formatted_date, "Volume": int(volume)})
            print(f"[LOG] Added {formatted_date} -> {volume}")

# Convert to DataFrame
df_stock = pd.DataFrame(all_data)

# Convert Date to datetime for proper range
df_stock["Date_dt"] = pd.to_datetime(df_stock["Date"], format="%m/%d/%Y")

# Create full daily date range for the requested period
start_dt = datetime.strptime(START_DATE, "%Y-%m-%d")
end_dt = datetime.strptime(END_DATE, "%Y-%m-%d")
all_dates = pd.date_range(start=start_dt, end=end_dt, freq="D")
df_all_dates = pd.DataFrame({"Date_dt": all_dates})

# Merge stock volumes onto full date range (missing days = NaN)
df_final = pd.merge(df_all_dates, df_stock[["Date_dt", "Volume"]], on="Date_dt", how="left")

# Format Date column
df_final["Date"] = df_final["Date_dt"].dt.strftime("%m/%d/%Y")
df_final = df_final[["Date", "Volume"]]

# Load existing CSV and append new data
try:
    df_existing = pd.read_csv("nvax_history4.csv")
    df_combined = pd.concat([df_existing, df_final], ignore_index=True)
except FileNotFoundError:
    df_combined = df_final

# Remove duplicates in case of overlap
df_combined = df_combined.drop_duplicates(subset=["Date"]).sort_values("Date", ascending=False).reset_index(drop=True)

# Save updated CSV
df_combined.to_csv("nvax_history4.csv", index=False)

print("\nUpdated CSV saved. Total rows:", len(df_combined))
