import csv
from datetime import datetime

def save_data(symbol, price, rsi):

    with open("market_data.csv", "a", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([datetime.now(), symbol, price, rsi])