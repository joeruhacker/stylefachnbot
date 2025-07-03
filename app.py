from flask import Flask, request, abort
from config import TELEGRAM_TOKEN, WEBHOOK_URL_BASE, WEBHOOK_URL_PATH, PORT
from bot.handlers import bot
from telebot.types import Update  # ← импорт правильного Update

app = Flask(__name__)

@app.get("/")
def index():
    return "OK", 200

@app.post(WEBHOOK_URL_PATH)
def telegram_webhook():
    if request.headers.get("content-type") == "application/json":
        data = request.get_data().decode('utf-8')
        update = Update.de_json(data)
        bot.process_new_updates([update])
        return "", 200
    abort(403)

def set_webhook():
    # При локальном тесте ngrok: замените WEBHOOK_URL_BASE на ваш ngrok-URL
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=PORT)