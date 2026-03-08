import requests

def get_usdt_symbols():

    url = "https://api.binance.com/api/v3/exchangeInfo"

    data = requests.get(url).json()

    symbols = []

    for item in data["symbols"]:

        symbol = item["symbol"]

        if symbol.endswith("USDT") and item["status"] == "TRADING":
            symbols.append(symbol)

    return symbols
