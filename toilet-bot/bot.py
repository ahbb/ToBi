import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import os

from config import API_URL

FASTAPI_GEOCODE_URL = "http://localhost:8000/reverse_geocode"
FASTAPI_NEAREST_URL = "http://localhost:8000/nearest"

load_dotenv()
BOT_TOKEN = os.getenv("BIDETBUDDY_TOKEN")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("Send Current Location 📍", request_location=True)],
        [KeyboardButton("ℹ️ About BidetBuddy")],
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=True
    )

    welcome_text = (
        "🏠 *Welcome to BidetBuddy!*\n\n"
        "I'm here to help you find the *nearest toilets with bidets* across Singapore 🇸🇬.\n\n"
        "To get started:\n"
        "➡️ Tap *Send Current Location* below\n"
        "…and I'll find the closest bidet-equipped toilets for you!\n"
        "Tip: For the most accurate location, tap 📎 → Location → Send My Current Location.\n\n"
    )

    await update.message.reply_text(welcome_text,reply_markup=reply_markup, parse_mode="Markdown")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "ℹ️ About BidetBuddy":
        await update.message.reply_text(
            "🚽 *About BidetBuddy*\n\n"
            "This bot helps you find the nearest toilets with bidets.\n"
            "Powered by data from toiletswithbidetsg (https://linktr.ee/toiletswithbidetsg) & community updates.\n",
            parse_mode="Markdown"
        )

# When user sends location
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_location = update.message.location

    # Send a finding message immediately
    finding_msg = await update.message.reply_text("Finding nearby toilets… 🔎")

    lat = user_location.latitude
    lon = user_location.longitude

    # Call FastAPI /nearest (top 3)
    resp = requests.get(FASTAPI_NEAREST_URL, params={"lat": lat, "lon": lon}).json()
    results = resp.get("results", [])

    if not results:
        await update.message.reply_text("❌ No toilets found nearby.")
        return

    message_lines = ["🚽 *Nearest Toilets with Bidet:* \n"]
    for idx, item in enumerate(results, start=1):
        toilet = item["toilet"]
        distance = item["distances"]

        # Get address from reverse geocoding
        try:
            geo_resp = requests.post(
                FASTAPI_GEOCODE_URL,
                json={"latitude": toilet['lat'],
                      "longitude": toilet['lon']}
            ).json()
            address = geo_resp.get("address", "Address not found")
        except Exception:
            address = ""

        # Add one toilet to message
        message_lines.append(
            f"{idx}️⃣ *{toilet['name']}*\n"
            f"📍 Address: {address}\n"
            f"🚶‍♂️ Approx *{distance}km* away\n"
        )

    message_text = "\n".join(message_lines)

    # Edit the "Finding…" message so it becomes the final result (only show finding message once)
    await finding_msg.edit_text(message_text, parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))

    # Location and text handlers
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()