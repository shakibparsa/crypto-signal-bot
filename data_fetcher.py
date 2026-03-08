import requests


def get_price(symbol):

    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

    data = requests.get(url).json()

    return float(data["price"])



def get_candles(symbol):

    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100"

    data = requests.get(url).json()

    prices = []
    volumes = []

    for candle in data:

        close_price = float(candle[4])
        volume = float(candle[5])

        prices.append(close_price)
        volumes.append(volume)

    return prices, volumes