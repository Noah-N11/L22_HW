import pandas as pd
import streamlit as st
import requests

# Header
st.title("Crypto Dashboard (CoinGecko)")

# Sidebar inputs
coin = st.sidebar.selectbox("Select Cryptocurrency", ["bitcoin", "ethereum", "dogecoin"])
days = st.sidebar.selectbox("Select time range (days)", [1, 7, 30, 90])

# Cached API Call
@st.cache_data
def fetch_data(coin_id, days):
   url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
   params = {"vs_currency": "usd", "days" : days}

   try:
      response = requests.get(url, params=params)
      response.raise_for_status()
      data = response.json()

      prices = data["prices"]
      df = pd.DataFrame(prices, columns=["timestamp", "price"])
      df["timestam"] = pd.to_datetime(df["timestamp"], unit="ms")

      return df

   except requests.exceptions.RequestException as e:
      st.error(f"API request failed: {e}")
      return None

df = fetch_data(coin, days)

if df is not None:
   # Time Series chart
   st.subheader(f"{coin.capitalize()} Price Over Time")
   df = df.set_index("timestamp")
   st.lie_chart(df["price"])

   current_price = df["price"].iloc[-1]
   old_price = df["price"].iloc[0]

   delta = current_price - old_price

   st.metric(
      label = "Current Price (USD)",
      value = f"${current_price:.2f}",
      delta=f"{delta:.2f}"
   )

# Top Coins
@st.cache_data
def fetch_top_coins():
   url = "https://api.coingecko.com/api/v3/coins/markets"
   params = {
      "vs_currency": "usd", 
      "order": "market_cap_desc",
      "per_page": 10
   }
   try:
      response = requests.get(url, params=params)
      response.raise_for_status()
      data = response.json()

      df = pd.DataFrame(data)
      return df[["name", "market_cap"]]
   
   except requests.exceptions.RequestException as e:
      st.error(f"API request failed: {e}")
      return None
   
top_df = fetch_top_coins()

if top_df is not None:
   # Chart
   st.subheader("Top 10 Coins by Market Cap")
   st.bar_chart(top_df.set_index("name"))

   # Table
   st.subheader("Market Data Table")
   st.dataframe(top_df)