import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import yfinance as yf
import pandas as pd

from utils.indicators import moving_average, rsi
from utils.signals import buy_sell_signal
from model.lstm_model import lstm_predict

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Invest Better Pro", layout="wide")

st.title("📈 Invest Better – Advanced Live Dashboard")

# ------------------ MANUAL REFRESH ------------------
if st.button("🔄 Refresh Dashboard"):
    st.rerun()

# ------------------ SECTORS ------------------
SECTORS = {
    "INDIA - IT": ["TCS.NS", "INFY.NS", "WIPRO.NS"],
    "INDIA - BANKING": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"],
    "INDIA - ENERGY": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS"],
    "US - TECH": ["AAPL", "MSFT", "TSLA", "GOOGL"],
    "US - ENERGY": ["XOM", "CVX"]
}

sector = st.sidebar.selectbox("Select Sector", list(SECTORS.keys()))
ticker = st.sidebar.selectbox("Select Company", SECTORS[sector])

# ------------------ LOAD DATA ------------------
stock = yf.Ticker(ticker)
data = stock.history(period="1y")

if data.empty:
    st.error("No data found")
    st.stop()

close = data["Close"]
ma20 = moving_average(close)
rsi_val = rsi(close)

signal = buy_sell_signal(rsi_val.iloc[-1], close.iloc[-1], ma20.iloc[-1])

# ------------------ CURRENCY SELECTION ------------------
currency = st.selectbox("Select Currency", ["USD ($)", "INR (₹)"])

base_price = close.iloc[-1]
display_price = base_price
currency_symbol = "$"

# Convert USD → INR if selected
if currency == "INR (₹)":
    try:
        usd_inr = yf.Ticker("USDINR=X").history(period="1d")["Close"].iloc[-1]
        display_price = base_price * usd_inr
        currency_symbol = "₹"
    except:
        st.warning("Currency conversion failed")
else:
    currency_symbol = "$"

# ------------------ METRICS ------------------
col1, col2, col3 = st.columns(3)

col1.metric("Current Price", f"{display_price:.2f} {currency_symbol}")
col2.metric("RSI", f"{rsi_val.iloc[-1]:.2f}")
col3.metric("Signal", signal)

# ------------------ CHARTS ------------------
st.subheader("📉 Price + Moving Average")
st.line_chart(pd.DataFrame({
    "Price": close,
    "MA20": ma20
}))

st.subheader("📊 RSI Indicator")
st.line_chart(rsi_val)

# ------------------ LSTM PREDICTION ------------------
st.subheader("🤖 LSTM Price Prediction")
pred_price = lstm_predict(close.values)
st.success(f"Predicted Next Price: {pred_price:.2f} {currency_symbol}")

# =====================================================
# ================== PAPER TRADING ====================
# =====================================================

st.subheader("💼 Paper Trading (Simulation)")

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

qty = st.number_input(
    "Quantity",
    min_value=1,
    max_value=10000,
    value=1,
    step=1
)

col_buy, col_sell = st.columns(2)

# ------------------ BUY ------------------
with col_buy:
    if st.button("🟢 BUY STOCK"):
        st.session_state.portfolio.append({
            "Stock": ticker,
            "Qty": qty,
            "Buy Price": base_price
        })
        st.success(f"Bought {qty} shares of {ticker}")
        st.rerun()

# ------------------ SELL ------------------
with col_sell:
    if st.button("🔴 SELL STOCK"):
        for item in st.session_state.portfolio:
            if item["Stock"] == ticker:
                st.session_state.portfolio.remove(item)
                st.warning(f"Sold {ticker}")
                st.rerun()
                break

# ------------------ PORTFOLIO DISPLAY ------------------
if st.session_state.portfolio:
    portfolio_df = pd.DataFrame(st.session_state.portfolio)

    current_prices = {}
    for stock_symbol in portfolio_df["Stock"].unique():
        latest_price = yf.Ticker(stock_symbol).history(period="1d")["Close"].iloc[-1]
        current_prices[stock_symbol] = latest_price

    portfolio_df["Current Price"] = portfolio_df["Stock"].map(current_prices)

    portfolio_df["P/L"] = (
        (portfolio_df["Current Price"] - portfolio_df["Buy Price"])
        * portfolio_df["Qty"]
    )

    st.subheader("📂 Portfolio Summary")
    st.dataframe(portfolio_df, use_container_width=True)

    total_pl = portfolio_df["P/L"].sum()
    st.metric("💰 Total Profit / Loss", f"{total_pl:.2f}")

else:
    st.info("No stocks in portfolio yet.")

# ------------------ RECENT DATA ------------------
st.subheader("📄 Recent Data")
st.dataframe(data.tail())
