from textblob import TextBlob
import yfinance as yf

def news_sentiment(ticker):
    stock = yf.Ticker(ticker)
    news = stock.news

    if not news:
        return "Neutral 😐", 0.0

    polarity = 0
    count = 0

    for item in news[:5]:
        analysis = TextBlob(item["title"])
        polarity += analysis.sentiment.polarity
        count += 1

    score = polarity / count

    if score > 0.1:
        return "Positive 🟢", score
    elif score < -0.1:
        return "Negative 🔴", score
    else:
        return "Neutral 🟡", score