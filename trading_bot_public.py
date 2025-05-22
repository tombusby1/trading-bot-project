# trading_bot.py

import os
import sys
import time
import json
import logging
import requests
import datetime
import traceback
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# ========= ENV & LOGGING =========
load_dotenv()
nltk.download('vader_lexicon')
logging.basicConfig(filename='trading_bot.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# ========= CONFIGURATION =========
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME")
PAIR = os.getenv("TRADING_PAIR", "BTC/USDT")
TRADE_AMOUNT_USD = float(os.getenv("TRADE_AMOUNT", 100))
INTERVAL = int(os.getenv("INTERVAL", 300))  # default: 5 minutes

EMAIL_NOTIFICATIONS = os.getenv("EMAIL_NOTIFICATIONS", "False").lower() == "true"
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

# ========= INIT SERVICES =========
sia = SentimentIntensityAnalyzer()

# Exchange integration loaded dynamically
def load_exchange():
    import ccxt
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    if not hasattr(ccxt, EXCHANGE_NAME):
        raise ValueError(f"Exchange '{EXCHANGE_NAME}' is not supported.")
    return getattr(ccxt, EXCHANGE_NAME)({
        'apiKey': api_key,
        'secret': api_secret
    })

exchange = load_exchange()

# ========= EMAIL =========
def send_email(subject, body):
    if not EMAIL_NOTIFICATIONS:
        return
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = TO_EMAIL
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, TO_EMAIL, msg.as_string())
        server.quit()
        logging.info(f"📧 Email sent: {subject}")
    except Exception as e:
        logging.error(f"Email error: {e}")

# ========= SENTIMENT ANALYSIS =========
def get_news_sentiment():
    try:
        html = requests.get("https://www.coindesk.com/", timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        headlines = [tag.get_text() for tag in soup.find_all("h4")]
        scores = [sia.polarity_scores(text)['compound'] for text in headlines]
        return sum(scores) / len(scores) if scores else 0
    except Exception as e:
        logging.error(f"Sentiment error: {e}")
        return 0

# ========= PRICE DATA & INDICATORS =========
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = -delta.clip(upper=0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_price_data():
    ohlc = exchange.fetch_ohlcv(PAIR, timeframe='5m', limit=100)
    df = pd.DataFrame(ohlc, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['rsi'] = compute_rsi(df['close'], 14)
    df['ma'] = df['close'].rolling(window=20).mean()
    df['macd'] = df['close'].ewm(span=12).mean() - df['close'].ewm(span=26).mean()
    return df

# ========= STRATEGY PLACEHOLDERS =========
def should_buy(df, sentiment):
    # Strategy logic hidden
    return False  # placeholder

def should_sell(df, sentiment):
    #  Strategy logic hidden
    return False  # placeholder

# ========= ORDER EXECUTION =========
def place_order(side, amount_usd):
    try:
        price = exchange.fetch_ticker(PAIR)['last']
        volume = round(amount_usd / price, 6)
        order = exchange.create_market_order(PAIR, side, volume)
        msg = f"✅ Order placed: {side.upper()} {volume} at ${price:.2f}"
        logging.info(msg)
        send_email(f"{side.upper()} ORDER", msg)
    except Exception as e:
        msg = f"❌ Order error: {e}"
        logging.error(msg)
        send_email("ORDER ERROR", msg)

# ========= HEALTH CHECK =========
def test_exchange_connection():
    try:
        ticker = exchange.fetch_ticker(PAIR)
        logging.info(f"✅ Exchange connection OK. Price: ${ticker['last']}")
    except Exception as e:
        msg = f"❌ API error: {e}"
        logging.error(msg)
        send_email("API ERROR", msg)

# ========= MAIN LOOP =========
def run_bot():
    test_exchange_connection()
    while True:
        try:
            logging.info(f"\n--- {datetime.datetime.now()} ---")
            df = get_price_data()
            sentiment = get_news_sentiment()
            logging.info(f"Sentiment: {sentiment:.3f}")

            if should_buy(df, sentiment):
                place_order('buy', TRADE_AMOUNT_USD)
            elif should_sell(df, sentiment):
                place_order('sell', TRADE_AMOUNT_USD)
            else:
                logging.info("🤖 No trade signal.")

        except Exception as e:
            msg = f"❗ Bot error: {e}\n{traceback.format_exc()}"
            logging.error(msg)
            send_email("BOT ERROR", msg)

        time.sleep(INTERVAL)

if __name__ == "__main__":
    run_bot()