def market_direction(price, average):

    if price > average:
        return "Market looks bullish"

    elif price < average:
        return "Market looks bearish"

    else:
        return "Market is neutral"