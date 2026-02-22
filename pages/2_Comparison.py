import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

st.title("Stock Comparison")

stocks = ["AAPL","MSFT","TSLA","GOOGL","AMZN"]

selected = st.multiselect("Select Stocks", stocks)

if selected:
    data = yf.download(selected, period="6mo")["Close"]

    fig, ax = plt.subplots()
    data.plot(ax=ax)
    st.pyplot(fig)