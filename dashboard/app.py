import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
from utils.indicators import calculate_rsi, calculate_ma

st.set_page_config(page_title="Invest Better", layout="wide", page_icon="📈")

st.title("Invest Better")
st.caption("AI Powered Stock Analysis Dashboard")
st.markdown("---")

stocks = ["AAPL","MSFT","TSLA","GOOGL","AMZN"]

if "selected_stock" in st.session_state:
    ticker = st.session_state.selected_stock
else:
    ticker = st.sidebar.selectbox("Choose Company", stocks)

data = yf.download(ticker, period="6mo")

data["RSI"] = calculate_rsi(data["Close"])
data["MA20"] = calculate_ma(data["Close"])

current_price = data["Close"].iloc[-1]
rsi = data["RSI"].iloc[-1]
ma20 = data["MA20"].iloc[-1]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Current Price", f"${current_price:.2f}")

with col2:
    st.metric("RSI", f"{rsi:.2f}")

with col3:
    st.metric("MA20", f"${ma20:.2f}")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["Overview", "Technical Indicators", "AI Prediction"])

with tab1:
    st.line_chart(data["Close"])

with tab2:
    fig, ax = plt.subplots()
    ax.plot(data["RSI"])
    ax.axhline(70)
    ax.axhline(30)
    ax.set_title("RSI")
    st.pyplot(fig)

with tab3:
    predicted_price = current_price * 1.02  # Dummy prediction
    confidence = abs(predicted_price - current_price) / current_price * 100

    st.subheader("Prediction")
    st.write(f"Predicted Price: ${predicted_price:.2f}")

    if predicted_price > current_price:
        st.success(f"Recommendation: BUY | Confidence: {confidence:.2f}%")
    else:
        st.error(f"Recommendation: SELL | Confidence: {confidence:.2f}%")