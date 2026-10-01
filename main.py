
    requests.post(url, json=payload)

def fetch_trending_sentiment():
    url = "https://finviz.com/news.ashx"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        news_items = [a.text.strip() for a in soup.find_all('a', class_='nn-tab-link')[:10]]
        return news_items
    except Exception as e:
        print(f"Fehler beim Laden der News: {e}")
        return []

def generate_stock_report():
    news = fetch_trending_sentiment()
    report = "📈 *Täglicher Markt- & Aktien-Radar* 🚀\n\n"
    report += "*Aktuelle Top-Schlagzeilen:*\n"
    if news:
        for idx, item in enumerate(news[:5], 1):
            report += f"{idx}. {item}\n"
    else:
        report += "Keine aktuellen Nachrichten gefunden.\n"
    report += "\n💡 *Hinweis:* Prüfe diese Werte heute auf erhöhtes Handelsvolumen."
    return report

if __name__ == "__main__":
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        msg = generate_stock_report()
        send_telegram_message(msg)
    else:
        print("Telegram-Zugangsdaten fehlen.")
