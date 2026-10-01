import os
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CACHE_FILE = "sent_news.txt"

# Signalwörter zur Analyse der Haltedauer
SHORT_TERM_KEYWORDS = ["earnings", "revenue", "soars", "plunges", "jump", "drop", "q1", "q2", "q3", "q4", "upgrade", "downgrade", "target price", "surge", "crash", "alert"]
LONG_TERM_KEYWORDS = ["dividend", "buyback", "acquisition", "merger", "annual", "growth", "partnership", "ceo", "expansion", "strategic", "invest"]

def classify_trade_type(title: str) -> str:
    """Prüft den Inhalt der Nachricht und gibt eine Empfehlung zur Haltedauer ab."""
    title_lower = title.lower()
    
    is_short = any(kw in title_lower for kw in SHORT_TERM_KEYWORDS)
    is_long = any(kw in title_lower for kw in LONG_TERM_KEYWORDS)
    
    if is_short:
        return "⚡ *Empfehlung:* Rather KURZFRISTIG halten (Trading / Momentum)"
    elif is_long:
        return "🛡 *Empfehlung:* Rather LANGFRISTIG halten (Buy & Hold / Investment)"
    else:
        return "📊 *Empfehlung:* MARKT-NEWS (Beobachten)"

def load_sent_news():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_sent_news(sent_hashes):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        for h in sent_hashes:
            f.write(f"{h}\n")

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload)

def fetch_latest_news():
    url = "https://finviz.com/news.ashx"
    headers = {'User-Agent': 'Mozilla/5.0'}
    news_items = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr', class_='nn-row')
        
        for row in rows[:10]:
            time_td = row.find('td', class_='nn-date')
            link_a = row.find('a', class_='nn-tab-link')
            
            if time_td and link_a:
                post_time = time_td.text.strip()
                title = link_a.text.strip()
                link = link_a.get('href', '')
                news_hash = hashlib.md5(title.encode('utf-8')).hexdigest()
                
                news_items.append({
                    'hash': news_hash,
                    'time': post_time,
                    'title': title,
                    'link': link
                })
    except Exception as e:
        print(f"Fehler beim Laden der News: {e}")
    
    return news_items

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram-Zugangsdaten fehlen.")
        exit(1)

    sent_hashes = load_sent_news()
    latest_news = fetch_latest_news()
    new_count = 0

    for news in reversed(latest_news):
        if news['hash'] not in sent_hashes:
            now_str = datetime.now().strftime("%H:%M Uhr")
            recommendation = classify_trade_type(news['title'])
            
            msg = f"🚨 *NEUE EILMELDUNG* ({now_str})\n\n"
            msg += f"📰 *Titel:* [{news['title']}]({news['link']})\n"
            msg += f"⏱ *Zeit:* {news['time']}\n\n"
            msg += f"{recommendation}\n\n"
            msg += "📱 *Trade Republic:* Suche den Namen in deiner App."
            
            send_telegram_message(msg)
            sent_hashes.add(news['hash'])
            new_count += 1

    if new_count > 0:
        save_sent_news(sent_hashes)
        print(f"{new_count} neue Nachricht(en) gesendet.")
    else:
        print("Keine neuen Nachrichten seit dem letzten Check.")
