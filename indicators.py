def simple_moving_average(prices, period):

    if len(prices) < period:
        return 0

    return sum(prices[-period:]) / period


def rsi(prices, period=14):

    if len(prices) < period + 1:
        return 50

    gains = []
    losses = []

    for i in range(1, period + 1):

        change = prices[-i] - prices[-i-1]

        if change > 0:
            gains.append(change)
        else:
            losses.append(abs(change))

    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))

    return rsi_value