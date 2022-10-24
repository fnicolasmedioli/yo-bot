import requests
import os

TELEGRAM_BOT_API_KEY = os.environ.get("TELEGRAM_BOT_API_KEY")

def send_message(text, chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_API_KEY}/sendMessage"

    payload = {
        "text": text,
        "chat_id": chat_id,
        "disable_web_page_preview": False,
        "disable_notification": False,
        "reply_to_message_id": None
    }

    headers = {
        "accept": "application/json",
        "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)",
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)