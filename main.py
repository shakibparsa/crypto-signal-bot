import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor
from flask import Flask

from output import show_coin
from indicators import simple_moving_average, rsi
from logic import market_direction
from data_fetcher import get_candles
from telegram_sender import send_message, send_photo
from chart_generator import create_chart


# ---------------- WEB SERVER ----------------

app = Flask(__name__)

@app.route("/")
def home():
    return "Crypto Analyzer running"

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()


# ---------------- KEEP SERVER AWAKE ----------------

def keep_alive():
    url = "https://crypto-signal-bot-o0dj.onrender.com"

    while True:
        try:
            requests.get(url)
            print("Self ping sent")
        except:
            print("Ping failed")

        time.sleep(600)

threading.Thread(target=keep_alive).start()


# ---------------- SETTINGS ----------------

SCAN_INTERVAL = 30
SIGNAL_SCORE = 3
ALERT_COOLDOWN = 600
MAX_WORKERS = 15

symbols = [
"BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","ADAUSDT","DOGEUSDT","AVAXUSDT","DOTUSDT","MATICUSDT",
"LINKUSDT","LTCUSDT","TRXUSDT","ATOMUSDT","NEARUSDT","APTUSDT","ARBUSDT","OPUSDT","INJUSDT","SUIUSDT",
"SEIUSDT","FILUSDT","AAVEUSDT","UNIUSDT","ICPUSDT","ETCUSDT","ALGOUSDT","VETUSDT","EGLDUSDT","FTMUSDT"
]

print("Crypto Analyzer Started")
print("Scanner started")
send_message("Server bot is running")
print("Total coins:", len(symbols))


# ---------------- ATR ----------------

def calculate_atr(prices, period=14):

    if len(prices) < period + 1:
        return 0

    trs = []

    for i in range(1, len(prices)):
        tr = abs(prices[i] - prices[i-1])
        trs.append(tr)

    atr = sum(trs[-period:]) / period
    return atr


# ---------------- ANALYSIS ----------------

def analyze_coin(symbol):

    try:

        data = get_candles(symbol)

        if not data:
            return None

        prices, volumes = data

        if len(prices) < 60 or len(volumes) < 60:
            return None

        sma20 = simple_moving_average(prices, 20)
        sma50 = simple_moving_average(prices, 50)

        if sma20 == 0:
            return None

        current_price = prices[-1]
        rsi_value = rsi(prices)

        distance = ((current_price - sma20) / sma20) * 100
        direction = market_direction(current_price, sma20)

        avg_volume = sum(volumes[-20:]) / 20
        current_volume = volumes[-1]

        volume_spike = current_volume > avg_volume * 2
        whale_volume = current_volume > avg_volume * 4

        recent_volume = sum(volumes[-5:])

        whale_accumulation = recent_volume > avg_volume * 5 and abs(distance) < 1
        whale_distribution = recent_volume > avg_volume * 5 and rsi_value > 65

        resistance = max(prices[-20:])
        support = min(prices[-20:])

        breakout_up = current_price > resistance
        breakout_down = current_price < support

        atr = calculate_atr(prices)
        avg_atr = calculate_atr(prices[:-10]) if len(prices) > 30 else atr

        high_volatility = atr > avg_atr * 1.5

        score = 0
        reasons = []

        if rsi_value < 30:
            score += 2
            reasons.append("RSI Oversold")

        if rsi_value > 70:
            score += 2
            reasons.append("RSI Overbought")

        if abs(distance) > 2:
            score += 1
            reasons.append("Far from Average")

        if volume_spike:
            score += 2
            reasons.append("Volume Spike")

        if whale_volume:
            score += 3
            reasons.append("Whale Volume")

        if whale_accumulation:
            score += 3
            reasons.append("Whale Accumulation")

        if whale_distribution:
            score += 3
            reasons.append("Whale Distribution")

        if breakout_up:
            score += 3
            reasons.append("Resistance Breakout")

        if breakout_down:
            score += 3
            reasons.append("Support Breakout")

        if high_volatility:
            score += 2
            reasons.append("ATR Volatility")

        trend = "UPTREND" if sma20 > sma50 else "DOWNTREND"

        return {
            "symbol": symbol,
            "price": current_price,
            "average": sma20,
            "average50": sma50,
            "rsi": rsi_value,
            "distance": distance,
            "trend": trend,
            "score": score,
            "reasons": reasons,
            "prices": prices
        }

    except Exception as e:
        print("Error analyzing", symbol, e)
        return None


# ---------------- MAIN LOOP ----------------

last_alert = {}

while True:

    start_time = time.time()

    best_coin = ""
    best_score = 0

    movers = []
    signals = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(analyze_coin, symbols))

    for data in results:

        if data is None:
            continue

        symbol = data["symbol"]

        movers.append((symbol, abs(data["distance"])))

        if data["score"] > best_score:
            best_score = data["score"]
            best_coin = symbol

        if data["score"] >= SIGNAL_SCORE:
            signals.append(data)

    signals.sort(key=lambda x: x["score"], reverse=True)
    signals = signals[:5]

    print("\n========== SIGNALS ==========")

    for s in signals:

        show_coin(s["symbol"], s["price"])

        print("Average:", round(s["average"],4))
        print("RSI:", round(s["rsi"]))
        print("Distance:", round(s["distance"],2),"%")
        print("Trend:", s["trend"])
        print("Score:", s["score"])
        print("Reasons:", ", ".join(s["reasons"]))
        print("============")


    for s in signals[:3]:

        symbol = s["symbol"]

        if symbol not in last_alert or time.time() - last_alert[symbol] > ALERT_COOLDOWN:

            message = f"""
🚨 MARKET SIGNAL

Coin: {symbol}

Price: {round(s["price"],4)}
RSI: {round(s["rsi"])}

Trend: {s["trend"]}

Distance: {round(s["distance"],2)}%

Score: {s["score"]}

Signals:
{", ".join(s["reasons"])}
"""

            chart_path = create_chart(s["prices"], symbol)

            send_message(message)
            send_photo(chart_path, symbol + " Chart")

            last_alert[symbol] = time.time()


    print("\nMarket Leader:", best_coin)
    print("Leader Score:", best_score)

    print("\nTOP 3 MOVERS")

    movers.sort(key=lambda x: x[1], reverse=True)

    for coin, dist in movers[:3]:
        print(coin, "-", round(dist,2), "%")


    scan_time = round(time.time() - start_time,2)

    print("\nScan time:", scan_time, "seconds")
    print("\nScanning again in", SCAN_INTERVAL, "seconds...\n")

    time.sleep(SCAN_INTERVAL)
