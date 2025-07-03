import telebot, requests
from config import TELEGRAM_TOKEN
from .state import Step
from .fashn import FashnClient
import re
from urllib.parse import urlparse

URL_RE = re.compile(r'https?://\S+')

bot   = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode="HTML")
fashn = FashnClient()

# упрощённое хранилище сессии: {chat_id: {step, model}}
user_state: dict[int, dict] = {}

@bot.message_handler(func=lambda m: m.text and URL_RE.match(m.text))
def handle_garment_url(m):
    cid = m.chat.id
    st = user_state.setdefault(cid, {"step": Step.WAITING_MODEL})
    if st["step"] is not Step.WAITING_GARMENT:
        return
    link = m.text.strip()
    try:
        resp = requests.get(link, timeout=10)
        resp.raise_for_status()
        garment_bytes = resp.content
    except Exception as e:
        return bot.send_message(cid, f"Не смог загрузить изображение по ссылке: {e}")
    bot.send_message(cid, "⏳ Генерирую…")
    st["step"] = Step.PROCESSING
    try:
        pred_id = fashn.run(st.pop("model"), garment_bytes)
        out_url = fashn.poll(pred_id)
        bot.send_photo(cid, out_url, caption="Готово! ✨")
    except Exception as e:
        bot.send_message(cid, f"⚠️ Ошибка: {e}")
    finally:
        st["step"] = Step.WAITING_MODEL
        bot.send_message(cid, "Хотите ещё примерить? Пришлите новое фото модели.")

def _dl(file_id: str) -> bytes:
    file_info = bot.get_file(file_id)
    url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
    return requests.get(url).content

@bot.message_handler(commands=["start"])
def start(m):
    user_state[m.chat.id] = {"step": Step.WAITING_MODEL}
    bot.send_message(m.chat.id, "👋 Привет! Пришли фото в полный рост.")

@bot.message_handler(content_types=["photo"])
def got_photo(m):
    cid = m.chat.id
    st  = user_state.setdefault(cid, {"step": Step.WAITING_MODEL})
    img = _dl(m.photo[-1].file_id)

    if st["step"] is Step.WAITING_MODEL:
        st["model"] = img
        st["step"]  = Step.WAITING_GARMENT
        bot.send_message(m.chat.id, "Отлично! Теперь фото одежды для примерки.")

    elif st["step"] is Step.WAITING_GARMENT:
        bot.send_message(m.chat.id, "⏳ Генерирую…")
        st["step"] = Step.PROCESSING
        try:
            pid = fashn.run(st.pop("model"), img)
            result_url = fashn.poll(pid)
            bot.send_photo(cid, result_url, caption="Готово! ✨")
        except Exception as e:
            bot.send_message(cid, f"⚠️ Ошибка: {e}")
        finally:
            st["step"] = Step.WAITING_MODEL
            bot.send_message(cid, "Хотите ещё примерку? Пришлите новое фото модели.")

    else:  # PROCESSING
        bot.send_message(m.chat.id, "⏳ Один момент, предыдущее изображение ещё обрабатывается…")

@bot.message_handler(func=lambda _: True)
def fallback(m):
    st = user_state.get(m.chat.id, {}).get("step", Step.WAITING_MODEL)
    msg = {
        Step.WAITING_MODEL:   "Пожалуйста, пришлите фото в полный рост 🙂",
        Step.WAITING_GARMENT: "Жду фото одежды для примерки.",
        Step.PROCESSING:      "Генерирую предыдущее изображение, подождите…",
    }[st]
    bot.send_message(m.chat.id, msg)