import json, os

from flask import Flask, request
import requests

# токен для идентификации бота
TOKEN = os.getenv('TOKEN')
print(TOKEN)

# базовый url для нашего бота
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# url для отправки сообщений
SEND_MESSAGE = BASE_URL + "/sendMessage"

# url для установки webhook'а
SET_WEBHOOK = BASE_URL + "/setWebhook"

app = Flask(__name__)
requests_count = 0
set_webhook_flag = True


# функция для сохранения json-данных в файле для отладки
def save_debug_info(data, file_name='debug.json'):
    with open(file_name, 'wt', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# функция для парсинга апдейта на предмет текстового сообщения
# возвращается кортежей вида (chat_id, text) если это текстовое сообщение
# в противном случае возвращается None
def parse_text_messages(update):
    # обрабатываем только обновления с сообщениями
    if "message" not in update:
        return None
    # обрабатываем только текстовые сообщения
    if "text" not in update["message"]:
        return None
    # извлекаем нужные данные
    chat_id = update["message"]["chat"]["id"]
    text = update["message"]["text"]
    return chat_id, text


# функция для парсинга апдейта на предмет callback_query
# возвращается кортежей вида (chat_id, data) если это callback_query
# в противном случае возвращается None
def parse_callback_query(update):
    # обрабатываем только обновления с сообщениями
    if "callback_query" not in update:
        return None
    # обрабатываем только текстовые сообщения
    if "message" not in update["callback_query"]:
        return None
    # обрабатываем сообщения c callback_query.data
    if "data" not in update["callback_query"]:
        return None

    # извлекаем нужные данные
    chat_id = update["callback_query"]["message"]["chat"]["id"]
    data = update["callback_query"]["data"]
    return chat_id, data


# отправляем текстовое сообщение в определенный чат
def send_text_message(chat_id, text):
    #
    keyboard = {
        "inline_keyboard": [[
            {
                "text": "Нажми на кнопку!!!",
                "callback_data": "Молодец. Давай еще раз!!!"
            },
        ]]
    }

    # параметры запроса getUpdates
    send_message_parameters = {
        'chat_id': chat_id,
        'text': text,
        'reply_markup': keyboard
    }

    # отправляем запрос с параметрами
    r = requests.get(SEND_MESSAGE, json=send_message_parameters)


# множество ранее обработанных обновлений
processed_update_id = set()


# проверка на то, что указанный идентификатор обновления уже был ранее обработанн
# Возвращается True если сообщение содержится во множестве обработанных сообщений
def check_duplicate(update_id):
    if update_id in processed_update_id:
        return True
    processed_update_id.add(update_id)
    # print(processed_update_id)
    return False


@app.route("/")
def hello():
    # обновляем количество запросов (для отладки)
    global requests_count
    global set_webhook_flag

    requests_count += 1

    # ответное сообщение
    return f'Main page: requests_count = {requests_count}'


@app.route("/webhook", methods=['POST'])
def webhook():
    # обновляем количество запросов (для отладки)
    global requests_count
    requests_count += 1

    # принимаем данные - объект типа "Update"
    update = request.json
    save_debug_info(update)
    print(update)

    # проверяем на дублирующее сообщение
    update_id = update["update_id"]
    if not check_duplicate(update_id):

        # Обрабатываем текстовые сообщения
        text_message_data = parse_text_messages(update)
        if text_message_data is not None:
            chat_id, text = text_message_data
            print(chat_id, text)
            send_text_message(chat_id, text.upper())

        # обрабатываем callback
        callback_data = parse_callback_query(update)
        if callback_data is not None:
            chat_id, data = callback_data
            print(chat_id, data)
            send_text_message(chat_id, data)

    # успешный код завершения (на самом деле важно что мы что-то вернули)
    return "OK"


if __name__ == "__main__":
    app.run(port=80)
