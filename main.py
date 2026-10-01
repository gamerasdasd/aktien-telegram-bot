import os
import sys
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

print(f"Token vorhanden: {bool(TELEGRAM_BOT_TOKEN)}")
print(f"Chat-ID vorhanden: {bool(TELEGRAM_CHAT_ID)}")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("FEHLER: Secrets fehlen in GitHub!")
    sys.exit(1)

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": "🧪 *DIREKTER TEST*: Dein Bot funktioniert!",
    "parse_mode": "Markdown"
}

response = requests.post(url, json=payload)
print(f"Telegram Server Antwort: {response.status_code}")
print(f"Antwort-Text: {response.text}")
