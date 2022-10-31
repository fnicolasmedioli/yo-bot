import requests
import os

telegramBotApiKey = os.environ.get("telegramBotApiKey")

def send_message(text, chat_id):

    if not telegramBotApiKey:
        print("telegramBotApiKey no encontrada")
        return

    url = f"https://api.telegram.org/bot{telegramBotApiKey}/sendMessage"

    payload = {
        "text": text,
        "chat_id": chat_id,
        "disable_web_page_preview": False,
        "disable_notification": False,
        "reply_to_message_id": None
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)