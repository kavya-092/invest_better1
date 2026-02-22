import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
from utils.indicators import calculate_rsi, calculate_ma
import pandas as pd
import numpy as np

st.set_page_config(page_title="Invest Better", layout="wide", page_icon="📈")

st.title("Invest Better")
st.caption("AI Powered Stock Analysis Dashboard")
st.markdown("---")

stocks = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN"]

# Sidebar Selection
ticker = st.sidebar.selectbox("Choose Company", stocks)

# Download Data
@st.cache_data
def load_data(symbol):
    return yf.download(symbol, period="6mo", progress=False)

data = load_data(ticker)

# Check if data loaded
if data is None or data.empty:
    st.error("Failed to load stock data. Try again later.")
    st.stop()

# Clean Data
data = data.dropna()

# Calculate Indicators
data["RSI"] = calculate_rsi(data["Close"])
data["MA20"] = calculate_ma(data["Close"])

# Drop NaN after indicator calculation
data = data.dropna()

if data.empty:
    st.error("Not enough data to calculate indicators.")
    st.stop()

# Safe Extraction
current_price = float(data["Close"].iloc[-1])
rsi = float(data["RSI"].iloc[-1])
ma20 = float(data["MA20"].iloc[-1])

# Display Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Current Price", f"${current_price:.2f}")

with col2:
    st.metric("RSI", f"{rsi:.2f}")

with col3:
    st.metric("MA20", f"${ma20:.2f}")

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["Overview", "Technical Indicators", "AI Prediction"])

# Overview
with tab1:
    st.subheader("Closing Price Trend")
    st.line_chart(data["Close"])

# Technical Indicators
with tab2:
    st.subheader("RSI Indicator")
    fig, ax = plt.subplots()
    ax.plot(data["RSI"])
    ax.axhline(70)
    ax.axhline(30)
    ax.set_title("RSI")
    st.pyplot(fig)

# AI Prediction (Dummy Logic)
with tab3:
    predicted_price = current_price * 1.02  # Dummy 2% increase
    confidence = abs(predicted_price - current_price) / current_price * 100

    st.subheader("Prediction")
    st.write(f"Predicted Price: ${predicted_price:.2f}")

    if predicted_price > current_price:
        st.success(f"Recommendation: BUY | Confidence: {confidence:.2f}%")
    else:
        st.error(f"Recommendation: SELL | Confidence: {confidence:.2f}%")