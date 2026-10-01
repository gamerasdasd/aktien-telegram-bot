import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str):
    """Sendet eine Nachricht an den Telegram-Chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload)

def fetch_finviz_news():
    """Holt Schlagzeilen & Veröffentlichungszeiten von Finviz."""
    url = "https://finviz.com/news.ashx"
    headers = {'User-Agent': 'Mozilla/5.0'}
    items = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        rows = soup.find_all('tr', class_='nn-row')
        for row in rows[:5]:
            time_td = row.find('td', class_='nn-date')
            link_a = row.find('a', class_='nn-tab-link')
            
            if time_td and link_a:
                post_time = time_td.text.strip()
                title = link_a.text.strip()
                items.append(f"⏱ *{post_time}* — {title}")
    except Exception as e:
        print(f"Fehler Finviz: {e}")
    
    return items

def generate_stock_report():
    now_str = datetime.now().strftime("%d.%m.%Y um %H:%M Uhr UTC")
    news_list = fetch_finviz_news()
    
    report = f"📈 *TÄGLICHER AKTIEN- & NEWS-RADAR* 🚀\n"
    report += f"🗓 *Stand:* {now_str}\n\n"
    report += "📰 *Aktuellste Eilmeldungen & Market-Moving News:*\n\n"
    
    if news_list:
        for idx, item in enumerate(news_list, 1):
            report += f"{idx}. {item}\n\n"
    else:
        report += "Keine aktuellen Nachrichten gefunden.\n\n"
        
    report += "💡 *Fokus:* Werte mit hohem Volumen und frischen News beobachten!"
    return report

if __name__ == "__main__":
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        msg = generate_stock_report()
        send_telegram_message(msg)
    else:
        print("Telegram-Zugangsdaten fehlen.")
