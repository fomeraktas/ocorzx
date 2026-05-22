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
        print("Telegram:", r.status_code)
    except Exception as e:
        print(f"Telegram error: {e}")

def check_reviews():
    headers = {
        "Content-Type": "application/vnd.api+json",
        "X-Auth-Token": KASPI_TOKEN,
        "Accept": "application/vnd.api+json"
    }
    
    # First test token with orders API
    try:
        print("Testing token with orders API...")
        url_orders = "https://kaspi.kz/shop/api/v2/orders?page[number]=0&page[size]=1"
        r = requests.get(url_orders, headers=headers, timeout=30)
        print(f"Orders API: {r.status_code}")
        
        if r.status_code != 200:
            send_telegram(f"❌ Kaspi token gecersiz! Status: {r.status_code}\nToken: {KASPI_TOKEN[:20]}...")
            return
            
        # Token works, now try reviews
        print("Trying reviews API...")
        url_rev = "https://kaspi.kz/shop/api/v2/reviews?page[number]=0&page[size]=20"
        r2 = requests.get(url_rev, headers=headers, timeout=30)
        print(f"Reviews API: {r2.status_code}, {r2.text[:300]}")
        
        if r2.status_code == 200:
            data = r2.json()
            reviews = data.get('data', [])
            bad = [rv for rv in reviews if rv.get('attributes',{}).get('rating',5) <= 3]
            
            if bad:
                for rv in bad:
                    a = rv.get('attributes', {})
                    stars = '⭐' * a.get('rating', 1)
                    send_telegram(
                        f"⚠️ <b>Плохой отзыв на Kaspi!</b>\n\n"
                        f"{stars} ({a.get('rating','?')}/5)\n"
                        f"🛍 <b>Товар:</b> {a.get('productName','—')}\n"
                        f"👤 <b>Автор:</b> {a.get('authorName','Аноним')}\n"
                        f"💬 {a.get('comment','—')}\n\n"
                        f"👉 https://merchant.kaspi.kz"
                    )
            else:
                send_telegram("✅ Kaspi Bot aktif!\nKotu yorum yok.")
        else:
            send_telegram(f"⚠️ Reviews API status: {r2.status_code}\nYorum API desteklenmiyor olabilir.")
            
    except Exception as e:
        print(f"Error: {e}")
        send_telegram(f"❌ Hata: {str(e)}")

if __name__ == "__main__":
    print(f"Starting: {datetime.now()}")
    check_reviews()
