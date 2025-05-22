import csv
import re
import os

# === CONFIGURATION ===
# Use environment variables or fallback to generic filenames
LOG_FILE = os.getenv("TRADING_BOT_LOG", "trading_bot.log")
CSV_FILE = os.getenv("TRADING_BOT_CSV", "trading_bot_data.csv")

# Regex pattern to parse log lines:
# Matches: date, time, and full message content
pattern = re.compile(r'(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}),\d+ - (.*)$')

rows = []

with open(LOG_FILE, "r", encoding="utf-8") as infile:
    for line in infile:
        match = pattern.search(line)
        if match:
            date_str, time_str, message = match.groups()

            # Initialize extracted values
            rsi = None
            macd = None
            price = None
            connection_status = None

            # Generic extraction of indicators from message text
            rsi_match = re.search(r'RSI[: ]+([\d.]+)', message)
            if rsi_match:
                rsi = rsi_match.group(1)

            macd_match = re.search(r'MACD[: ]+([-.\d]+)', message)
            if macd_match:
                macd = macd_match.group(1)

            price_match = re.search(r'Price[: ]+\$?([\d,.]+)', message)
            if price_match:
                price = price_match.group(1)

            # Generic connection status detection (not exchange-specific)
            if re.search(r'connection (OK|Successful|Established)', message, re.IGNORECASE):
                connection_status = "OK"
            elif re.search(r'(API|connection) (error|failed|issue)', message, re.IGNORECASE):
                connection_status = "ERROR"

            # Compose row dictionary
            row = {
                "Date": date_str,
                "Time": time_str,
                "RSI": rsi,
                "MACD": macd,
                "Connection Status": connection_status,
                "Price": price,
                "Message": message.strip()
            }
            rows.append(row)

# Write parsed data to CSV
with open(CSV_FILE, "w", newline="", encoding="utf-8") as outfile:
    fieldnames = ["Date", "Time", "RSI", "MACD", "Connection Status", "Price", "Message"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"CSV file created: {CSV_FILE}")