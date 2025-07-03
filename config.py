# --- секреты ---
TELEGRAM_TOKEN = '7991938170:AAHtDQiGq4jEn-lLmSnJ4OU0yszFD_n6dUs'
FASHN_API_KEY  = 'fa-VdHFUoqU9ahr-ru741yTqKlb25rLdRWQ86OFk'

# --- сеть ---
# На тесте (ngrok) подменяйте это на https://<твой-.ngrok.app>
WEBHOOK_URL_BASE = 'https://59ea-85-16-128-158.ngrok-free.app'   # ← поменяйте в продакшне
WEBHOOK_URL_PATH = f"/bot/{TELEGRAM_TOKEN}"

# Локальный порт, который будете пробрасывать через ngrok
PORT = 8080