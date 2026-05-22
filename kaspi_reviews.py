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
            "text": msg
        }, timeout=10)
        print("Telegram:", r.status_code, r.text[:100])
    except Exception as e:
        print(f"Telegram error: {e}")

def check_kaspi_reviews():
    headers = {
        "Content-Type": "application/vnd.api+json",
        "X-Auth-Token": KASPI_TOKEN,
        "Accept": "application/vnd.api+json"
    }
    
    # Correct Kaspi reviews endpoint
    endpoints = [
        "https://kaspi.kz/shop/api/v2/reviews?page[number]=0&page[size]=50",
        "https://kaspi.kz/shop/api/v1/reviews?page[number]=0&page[size]=50",
        "https://kaspi.kz/shop/api/v2/merchant-reviews?page[number]=0&page[size]=50",
    ]
    
    for url in endpoints:
        try:
            print(f"Trying: {url}")
            r = requests.get(url, headers=headers, timeout=30)
            print(f"Status: {r.status_code}, Response: {r.text[:200]}")
            
            if r.status_code == 200:
                data = r.json()
                reviews = data.get('data', [])
                bad = [rv for rv in reviews if rv.get('attributes', {}).get('rating', 5) <= 3]
                
                if bad:
                    for rv in bad:
                        a = rv.get('attributes', {})
                        rating = a.get('rating', 1)
                        stars = '* ' * int(rating)
                        msg = (
                            f"PLOHOY OTZYV NA KASPI!\n\n"
                            f"Reyting: {rating}/5\n"
                            f"Tovar: {a.get('productName', '-')}\n"
                            f"Avtor: {a.get('authorName', 'Anonimnyy')}\n"
                            f"Otzyv: {a.get('comment', '-')}\n\n"
                            f"Otvetit: https://merchant.kaspi.kz"
                        )
                        send_telegram(msg)
                    return f"Naydeno {len(bad)} plohikh otzyvov"
                else:
                    send_telegram("Kaspi Bot aktif! Plohikh otzyvov net.")
                    return "Plohikh otzyvov net"
        except Exception as e:
            print(f"Error with {url}: {e}")
    
    send_telegram("Kaspi Reviews API ne dostupno. Proverite token.")
    return "API ne dostupno"

if __name__ == "__main__":
    print(f"Starting: {datetime.now()}")
    result = check_kaspi_reviews()
    print(f"Result: {result}")
