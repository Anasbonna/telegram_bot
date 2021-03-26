import json

import requests
from flask import Flask, request

# токен для идентификации бота
TOKEN = ""

# базовый url для нашего бота
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# url для отправки сообщений
SEND_MESSAGE = BASE_URL + "/sendMessage"

# url для установки webhook'а
SET_WEBHOOK = BASE_URL + "/setWebhook"

# параметры запроса
set_webhook_parameters = {
    'url': "https://a7ad989ce8a6.ngrok.io" + '/webhook',
}

# устанавливаем webhook
r = requests.get(SET_WEBHOOK, json=set_webhook_parameters)
print(r.json())
