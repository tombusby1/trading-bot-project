# Trading Bot Project

A solo developer project running on a Raspberry Pi that uses Python and real-time market & sentiment data to automatically trade Bitcoin via an Exchange's API. A native SwiftUI iOS app is also in development to visualize trade logs and performance.

> Note: This repository excludes any proprietary strategy logic, API credentials, and private data.

---

## Overview

This bot connects to an exchange to fetch 5-minute OHLCV data, computes technical indicators (RSI, MACD, MA), performs real-time sentiment analysis on crypto headlines from Coindesk using NLTK VADER, and places live buy/sell market orders based on combined signals. It also logs all decision points and errors to a `.log` file, and can send notifications via email.

---

## Tech Stack

### Python Bot (Raspberry Pi)
- `ccxt` & `pyexchangeapi`: Exchange API integration
- `pandas`, `numpy`: Data manipulation and indicators
- `nltk`, `BeautifulSoup`: Sentiment analysis of headlines
- `smtplib`: Email alerts
- `logging`, `traceback`: Diagnostics & error logging

### Companion iOS App (WIP)
- SwiftUI with MVVM architecture
- CSV parsing and visualization of trade logs
- Live insights on bot decisions, sentiment trends, and market moves

---

## Features

- ✅ Fetch live 5-min BTC/USDT OHLC data from the Exchange
- ✅ Calculate RSI, MACD, Moving Average
- ✅ Scrape Coindesk headlines and compute sentiment score
- ✅ Decision engine for buy/sell/hold logic (abstracted)
- ✅ Execute live market orders (buy/sell) via the Exchange
- ✅ Log all data points and bot actions
- ✅ Email alerts for trade execution & exceptions
- ✅ Convert `.log` to `.csv` via script for visualization
- 🧪 Backtest mode (in progress)
- 📊 SwiftUI dashboard to track bot data (in progress)

---

## Security & Privacy

- API credentials are loaded from environment variables or local `.key` file.
- `.env`, `.key`, and strategy logic are excluded from the repository.
- Live trading logic is redacted for confidentiality.
- The repository includes a `.env.example` file as a template.

---

## 📁 Repo Structure

```
trading-bot-project/
├── trading_bot.py           # Core bot logic
├── log_to_csv.py            # Parses log into structured CSV
├── morning_report.py        # Summary/reporting script
├── .gitignore
├── README.md
├── requirements.txt
└── ios-companion-app/       # SwiftUI app (structure outlined below)

ios-companion-app/
├── TradingLogView.swift
├── TradingLogEntry.swift
├── TradingLogModel.swift
├── AddLogView.swift
├── SettingsView.swift
├── CSVLoader.swift
└── Resources/
    └── trading_bot_data.csv
```


---

## 🧪 Example: Log Entry Format

2024-07-01 08:00:00 - Price: $75000.00 | RSI: 28.4 | MACD: 120.3 | MA: 74995 | Sentiment: 0.18 📈 Buy signal triggered ✅ Order placed: BUY 0.001542 BTC at $75000.00
