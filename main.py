import json
import logging
import os
import sys

import requests
from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
BOT_TOKEN   = os.getenv("BOT_TOKEN", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "astrosecret123")
DEFAULT_TZ  = os.getenv("DEFAULT_TZ_OFFSET", "+03:00")
DEFAULT_LAT = os.getenv("DEFAULT_LAT", "55.7558")
DEFAULT_LON = os.getenv("DEFAULT_LON", "37.6176")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__, static_folder="public")

# ── Mini App (frontend) ───────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("public", "index.html")

# ── API: horoscope ────────────────────────────────────────────────────────────
@app.route("/api/horoscope")
def horoscope():
    sign  = request.args.get("sign", "")
    htype = request.args.get("type", "day")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from services.parser import get_daily_horoscope, get_weekly_horoscope
        text = get_weekly_horoscope(sign) if htype == "week" else get_daily_horoscope(sign)
    except Exception as e:
        log.error("horoscope error: %s", e)
        text = "Гороскоп временно недоступен. Попробуйте позже."
    return jsonify({"text": text})

# ── API: natal chart ──────────────────────────────────────────────────────────
@app.route("/api/natal", methods=["POST", "OPTIONS"])
def natal():
    if request.method == "OPTIONS":
        return _cors_response()
    try:
        body = request.get_json(force=True) or {}
        birthdate = body.get("birthdate", "")
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from services.natal import build_natal_report
        report = build_natal_report(birthdate)
        resp = jsonify({"report": report})
    except Exception as e:
        log.error("natal error: %s", e)
        resp = jsonify({"error": str(e)})
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

def _cors_response():
    r = jsonify({})
    r.headers["Access-Control-Allow-Origin"] = "*"
    r.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    r.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return r

# ── Telegram webhook ──────────────────────────────────────────────────────────
@app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    data = request.get_json(force=True) or {}
    try:
        _handle_update(data)
    except Exception as e:
        log.error("webhook handler error: %s", e)
    return "ok"

def _handle_update(data):
    msg = data.get("message") or data.get("edited_message")
    if not msg:
        return
    chat_id = msg["chat"]["id"]
    text    = msg.get("text", "")
    if text.startswith("/start"):
        _send_start(chat_id)

def _send_start(chat_id):
    app_url = os.getenv("MINI_APP_URL", "")
    if not app_url:
        _tg_post("sendMessage", {"chat_id": chat_id, "text": "MINI_APP_URL не настроен."})
        return
    payload = {
        "chat_id": chat_id,
        "text": "Ваш личный астролог.\nНажмите кнопку чтобы открыть приложение.",
        "reply_markup": json.dumps({
            "inline_keyboard": [[{
                "text": "Открыть Astro ✨",
                "web_app": {"url": app_url}
            }]]
        })
    }
    _tg_post("sendMessage", payload)

def _tg_post(method, payload):
    try:
        r = requests.post(f"{TELEGRAM_API}/{method}", data=payload, timeout=10)
        log.info("TG %s -> %s", method, r.status_code)
    except Exception as e:
        log.error("TG request failed: %s", e)

# ── Setup webhook (вызывается один раз после деплоя) ─────────────────────────
@app.route("/setup")
def setup():
    host = request.host_url.rstrip("/")
    webhook_url = f"{host}/webhook/{WEBHOOK_SECRET}"
    r = requests.get(
        f"{TELEGRAM_API}/setWebhook",
        params={"url": webhook_url, "drop_pending_updates": True},
        timeout=10
    )
    result = r.json()
    log.info("setWebhook result: %s", result)
    return jsonify(result)

# ── Health check ──────────────────────────────────────────────────────────────
@app.route("/health")
def health():
    return "ok"

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
