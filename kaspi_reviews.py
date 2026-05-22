import requests
import json
import os
from datetime import datetime, timedelta

KASPI_TOKEN = os.environ.get('KASPI_TOKEN')
TG_BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')
TG_CHAT_ID = os.environ.get('TG_CHAT_ID')

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TG_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    })

def check_reviews():
    # Get reviews from last 24 hours
    now = int(datetime.now().timestamp() * 1000)
    yesterday = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)
    
    url = "https://kaspi.kz/shop/api/v2/reviews"
    headers = {
        "Content-Type": "application/vnd.api+json",
        "X-Auth-Token": KASPI_TOKEN
    }
    params = {
        "page[number]": 0,
        "page[size]": 50,
        "filter[reviews][creationDate][$ge]": yesterday,
        "filter[reviews][creationDate][$le]": now
    }
    
    try:
        resp = requests.get(url, headers=headers, params=params)
        data = resp.json()
        
        bad_reviews = []
        reviews = data.get('data', [])
        
        for review in reviews:
            attrs = review.get('attributes', {})
            rating = attrs.get('rating', 5)
            
            if rating <= 3:
                bad_reviews.append({
                    'rating': rating,
                    'comment': attrs.get('comment', '—'),
                    'product': attrs.get('productName', '—'),
                    'author': attrs.get('authorName', 'Аноним'),
                    'date': attrs.get('creationDate', '')
                })
        
        if bad_reviews:
            for r in bad_reviews:
                stars = '⭐' * r['rating']
                msg = (
                    f"⚠️ <b>Плохой отзыв на Kaspi!</b>\n\n"
                    f"{stars} ({r['rating']}/5)\n"
                    f"🛍 <b>Товар:</b> {r['product']}\n"
                    f"👤 <b>Автор:</b> {r['author']}\n"
                    f"💬 <b>Отзыв:</b> {r['comment']}\n\n"
                    f"👉 Ответьте на отзыв: https://merchant.kaspi.kz"
                )
                send_telegram(msg)
        else:
            print("Нет плохих отзывов за последние 24 часа")
            
    except Exception as e:
        send_telegram(f"⚠️ Ошибка при проверке отзывов: {str(e)}")
        print(f"Error: {e}")

if __name__ == "__main__":
    check_reviews()
