import requests
import os
from datetime import datetime

TG_BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')
TG_CHAT_ID = os.environ.get('TG_CHAT_ID')
KASPI_TOKEN = os.environ.get('KASPI_TOKEN')

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={
            "chat_id": TG_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML"
        }, timeout=10)
        print("Telegram:", r.status_code, r.text[:100])
    except Exception as e:
        print(f"Telegram error: {e}")

def get_updates():
    """Telegram'dan gelen mesajları al"""
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getUpdates"
    r = requests.get(url, timeout=10)
    return r.json().get('result', [])

def check_kaspi_reviews():
    headers = {
        "Content-Type": "application/vnd.api+json",
        "X-Auth-Token": KASPI_TOKEN,
        "Accept": "application/vnd.api+json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        # Try reviews endpoint
        url = "https://kaspi.kz/shop/api/v2/reviews?page[number]=0&page[size]=50"
        r = requests.get(url, headers=headers, timeout=60)
        print(f"Reviews API: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            reviews = data.get('data', [])
            bad = [rv for rv in reviews if rv.get('attributes', {}).get('rating', 5) <= 3]
            
            if bad:
                for rv in bad:
                    a = rv.get('attributes', {})
                    stars = '⭐' * int(a.get('rating', 1))
                    send_telegram(
                        f"⚠️ <b>Плохой отзыв!</b>\n\n"
                        f"{stars} ({a.get('rating', '?')}/5)\n"
                        f"🛍 <b>Товар:</b> {a.get('productName', '—')}\n"
                        f"👤 <b>Автор:</b> {a.get('authorName', 'Аноним')}\n"
                        f"💬 {a.get('comment', '—')}\n\n"
                        f"👉 https://merchant.kaspi.kz"
                    )
                return f"Найдено {len(bad)} плохих отзывов"
            else:
                return "Плохих отзывов нет ✅"
        else:
            return f"API ответил: {r.status_code} - {r.text[:200]}"
            
    except Exception as e:
        return f"Ошибка: {str(e)}"

def handle_commands():
    """Telegram komutlarını işle"""
    updates = get_updates()
    for update in updates:
        msg = update.get('message', {})
        text = msg.get('text', '')
        chat_id = msg.get('chat', {}).get('id', '')
        
        if text == '/yorumlar' or text == '/reviews':
            send_telegram("🔄 Проверяю отзывы на Kaspi...")
            result = check_kaspi_reviews()
            send_telegram(f"📊 Результат: {result}")
        elif text == '/start':
            send_telegram(
                "👋 <b>Kaspi Reviews Bot</b>\n\n"
                "Команды:\n"
                "/yorumlar — проверить отзывы\n"
                "/start — помощь"
            )

if __name__ == "__main__":
    print(f"Starting: {datetime.now()}")
    # Check for commands first
    handle_commands()
    # Then auto check reviews
    result = check_kaspi_reviews()
    print(f"Result: {result}")
    if "Ошибка" in result or "API" in result:
        send_telegram(f"🤖 Kaspi Bot:\n{result}")
