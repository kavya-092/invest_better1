def buy_sell_signal(rsi_value):
    if rsi_value < 30:
        return "BUY 🟢"
    elif rsi_value > 70:
        return "SELL 🔴"
    else:
        return "HOLD 🟡"