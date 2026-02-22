import streamlit as st
import yfinance as yf
from utils.indicators import calculate_rsi

st.title("Company Overview")

companies = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "Google": "GOOGL",
    "Amazon": "AMZN"
}

cols = st.columns(3)

for i, (name, ticker) in enumerate(companies.items()):
    data = yf.download(ticker, period="3mo")
    price = data["Close"].iloc[-1]
    data["RSI"] = calculate_rsi(data["Close"])
    rsi = data["RSI"].iloc[-1]

    with cols[i % 3]:
        st.metric(name, f"${price:.2f}")
        st.write(f"RSI: {rsi:.2f}")

        if st.button(f"View {name}", key=name):
            st.session_state.selected_stock = ticker
            st.switch_page("dashboard/app.py")