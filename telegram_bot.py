import os
import httpx
import logging

from dotenv import load_dotenv
from telegram import Update
from telegram.request import HTTPXRequest
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AGENT_URL = os.getenv("AGENT_URL", "http://127.0.0.1:8000/message")
PROXY_URL = os.getenv("TELEGRAM_PROXY", "socks5h://172.22.0.1:10808")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋\nمن دستیار هوشمند شما هستم.\nپیامت رو بفرست."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text

    print(f"📩 Message received: {message}")

    try:
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                AGENT_URL,
                json={
                    "customer_id": str(update.effective_user.id),
                    "message": message,
                },
            )

            print(f"Agent status: {response.status_code}")
            print(f"Agent response body: {response.text}")

            response.raise_for_status()
            answer = response.json()["ai_response"]

    except Exception as e:
        logging.exception("Agent request failed")
        answer = f"خطا در ارتباط با ایجنت: {type(e).__name__}"

    await update.message.reply_text(answer)


def main():
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

    telegram_request = HTTPXRequest(
        proxy=PROXY_URL,
        http_version="1.1",
        connect_timeout=60,
        read_timeout=90,
        write_timeout=60,
        pool_timeout=60,
    )

    get_updates_request = HTTPXRequest(
        proxy=PROXY_URL,
        http_version="1.1",
        connect_timeout=60,
        read_timeout=90,
        write_timeout=60,
        pool_timeout=60,
    )

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .request(telegram_request)
        .get_updates_request(get_updates_request)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Telegram bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
