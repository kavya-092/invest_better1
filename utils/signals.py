def buy_sell_signal(rsi_value, price, ma):
    if rsi_value < 30 and price > ma:
        return "BUY 🟢"
    elif rsi_value > 70:
        return "SELL 🔴"
    else:
        return "HOLD 🟡"
