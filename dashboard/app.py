import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

from utils.indicators import calculate_ma, calculate_rsi
from utils.signals import buy_sell_signal
from model.lstm_model import lstm_predict

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Invest Better Pro", layout="wide", page_icon="📈")

st.title("📈 Invest Better – Advanced Live Dashboard")
st.markdown("---")

# ------------------ REFRESH BUTTON ------------------
if st.button("🔄 Refresh Dashboard"):
    st.cache_data.clear()
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
@st.cache_data
def load_data(symbol):
    stock = yf.Ticker(symbol)
    return stock.history(period="1y")

data = load_data(ticker)

if data.empty:
    st.error("No data found.")
    st.stop()

close = data["Close"]
ma20 = calculate_ma(close)
rsi_val = calculate_rsi(close)

signal = buy_sell_signal(rsi_val.iloc[-1], close.iloc[-1], ma20.iloc[-1])

# ------------------ CURRENCY ------------------
currency = st.sidebar.selectbox("Select Currency", ["USD ($)", "INR (₹)"])

base_price = close.iloc[-1]
display_price = base_price
currency_symbol = "$"

if currency == "INR (₹)":
    try:
        usd_inr = yf.Ticker("USDINR=X").history(period="1d")["Close"].iloc[-1]
        display_price = base_price * usd_inr
        currency_symbol = "₹"
    except:
        st.warning("Currency conversion failed")

# ------------------ TOP METRICS ------------------
col1, col2, col3 = st.columns(3)

col1.metric("Current Price", f"{display_price:.2f} {currency_symbol}")
col2.metric("RSI", f"{rsi_val.iloc[-1]:.2f}")
col3.metric("Signal", signal)

st.markdown("---")

# ================== TABS ==================
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Overview", "📈 Technical Indicators", "🤖 AI Prediction", "💼 Paper Trading"]
)

# ================== OVERVIEW ==================
with tab1:
    st.subheader("Price & Moving Average")

    fig, ax = plt.subplots()
    ax.plot(close, label="Price")
    ax.plot(ma20, label="MA20")
    ax.legend()
    st.pyplot(fig)

# ================== INDICATORS ==================
with tab2:
    st.subheader("RSI Indicator")

    fig2, ax2 = plt.subplots()
    ax2.plot(rsi_val, label="RSI")
    ax2.axhline(70)
    ax2.axhline(30)
    ax2.legend()
    st.pyplot(fig2)

# ================== AI PREDICTION ==================
with tab3:
    st.subheader("LSTM Prediction (Next Step)")

    pred_price = lstm_predict(close.values)

    fig3, ax3 = plt.subplots()
    ax3.plot(close.index, close, label="Real Price")
    ax3.scatter(close.index[-1], pred_price, label="Predicted Next Price")
    ax3.legend()
    st.pyplot(fig3)

    st.success(f"Predicted Next Price: {pred_price:.2f} {currency_symbol}")

# ================== PAPER TRADING ==================
with tab4:
    st.subheader("Simulation Trading")

    if "portfolio" not in st.session_state:
        st.session_state.portfolio = []

    qty = st.number_input("Quantity", min_value=1, max_value=10000, value=1)

    col_buy, col_sell = st.columns(2)

    with col_buy:
        if st.button("🟢 BUY"):
            st.session_state.portfolio.append({
                "Stock": ticker,
                "Qty": qty,
                "Buy Price": base_price
            })
            st.success("Stock Bought")
            st.rerun()

    with col_sell:
        if st.button("🔴 SELL"):
            for item in st.session_state.portfolio:
                if item["Stock"] == ticker:
                    st.session_state.portfolio.remove(item)
                    st.warning("Stock Sold")
                    st.rerun()
                    break

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

        st.dataframe(portfolio_df, use_container_width=True)

        total_pl = portfolio_df["P/L"].sum()
        st.metric("Total Profit / Loss", f"{total_pl:.2f}")

    else:
        st.info("No stocks in portfolio yet.")