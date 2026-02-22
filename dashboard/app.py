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


# ------------------ LOAD DATA (FIXED ⭐) ------------------
@st.cache_data(ttl=60)
def load_data(symbol):
    data = yf.download(symbol, period="1y", progress=False)

    # ⭐ FIX multi index columns (yfinance new bug)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return data


data = load_data(ticker)

if data is None or data.empty:
    st.error("❌ No data found. Try another stock.")
    st.stop()

close = data["Close"]


# ------------------ INDICATORS ------------------
ma20 = moving_average(close)
rsi_val = rsi(close)

# ⭐ FIXED signal call
signal = buy_sell_signal(rsi_val.iloc[-1])


# ------------------ METRICS ------------------
col1, col2, col3 = st.columns(3)

col1.metric("Current Price", f"{close.iloc[-1]:.2f}")
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

try:
    pred_price = lstm_predict(close.values)
    st.success(f"Predicted Next Price: {pred_price:.2f}")
except:
    st.warning("LSTM prediction failed.")


# =====================================================
# ================== PAPER TRADING ====================
# =====================================================

st.subheader("💼 Paper Trading (Simulation)")

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

qty = st.number_input("Quantity", min_value=1, max_value=10000, value=1, step=1)

col_buy, col_sell = st.columns(2)

# BUY
with col_buy:
    if st.button("🟢 BUY STOCK"):
        st.session_state.portfolio.append({
            "Stock": ticker,
            "Qty": qty,
            "Buy Price": close.iloc[-1]
        })
        st.success(f"Bought {qty} shares of {ticker}")
        st.rerun()

# SELL
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
        latest_data = yf.download(stock_symbol, period="1d", progress=False)

        # ⭐ FIX multi index
        if isinstance(latest_data.columns, pd.MultiIndex):
            latest_data.columns = latest_data.columns.get_level_values(0)

        if not latest_data.empty:
            current_prices[stock_symbol] = latest_data["Close"].iloc[-1]
        else:
            current_prices[stock_symbol] = portfolio_df.loc[
                portfolio_df["Stock"] == stock_symbol, "Buy Price"
            ].iloc[0]

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