import matplotlib.pyplot as plt

def create_chart(prices, symbol):

    plt.figure(figsize=(10,5))
    plt.plot(prices)

    plt.title(symbol)
    plt.xlabel("Time")
    plt.ylabel("Price")

    filename = f"{symbol}_chart.png"

    plt.savefig(filename)
    plt.close()

    return filename