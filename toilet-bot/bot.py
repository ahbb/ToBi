import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import os
from fastapi import FastAPI, Request
from utils import load_toilets, find_k_nearest_toilets
from pydantic import BaseModel
from geopy.geocoders import Nominatim
import urllib.parse

# Command in render: python -m uvicorn bot:app --reload --port $PORT --host 0.0.0.0

# Local
FASTAPI_GEOCODE_URL = "http://localhost:8000/reverse_geocode"
FASTAPI_NEAREST_URL = "http://localhost:8000/nearest"

# Deployed
FASTAPI_GEOCODE_URL_LIVE = "https://tobi-4qvm.onrender.com/reverse_geocode"
FASTAPI_NEAREST_URL_LIVE = "https://tobi-4qvm.onrender.com/nearest"

# =====================
# FastAPI setup
# =====================
app = FastAPI()
geolocator = Nominatim(user_agent="BidetBuddyBot")
TOILETS = load_toilets()

# =====================
# Telegram setup
# =====================
load_dotenv()
BOT_TOKEN = os.getenv("BIDETBUDDY_TOKEN")
BOT_TOKEN_ENCODED = urllib.parse.quote(BOT_TOKEN, safe='')
WEBHOOK_URL = f"https://tobi-4qvm.onrender.com/telegram/webhook/{BOT_TOKEN_ENCODED}"

tg_app = ApplicationBuilder().token(BOT_TOKEN).build()

# =====================
# Models
# =====================
class Location(BaseModel):
    latitude: float
    longitude: float


# =====================
# Telegram handlers
# =====================
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
    resp = requests.get(FASTAPI_NEAREST_URL_LIVE, params={"lat": lat, "lon": lon}).json()
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
                FASTAPI_GEOCODE_URL_LIVE,
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
    await finding_msg.edit_text(message_text, parse_mode="Markdown")\

# Telegram handlers
tg_app.add_handler(CommandHandler("start", start))
# Location and text handlers
tg_app.add_handler(MessageHandler(filters.LOCATION, handle_location))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))


# =====================
# FastAPI endpoints
# =====================
@app.get("/")
def root():
    return {"status": "ok", "total_toilets": len(TOILETS)}

@app.get("/all")
def all_toilets():
    return TOILETS

@app.get("/nearest")
def nearest(lat: float, lon: float, k: int = 3):
    results = find_k_nearest_toilets(lat, lon, TOILETS, k)

    output = []
    for toilet, dist in results:
        output.append({
            "toilet": toilet,
            "distances": round(dist, 2)
        })

    return {"results": output}

# Lat long -> Address
@app.post("/reverse_geocode")
def reverse_geocode(loc: Location):
    try:
        result = geolocator.reverse((loc.latitude, loc.longitude))
        return {"address": result.address}
    except Exception:
        return {"address": ""} # If geocode fails, return empty string

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "BidetBuddy API"
    }


# =====================
# Webhook lifecycle
# =====================
@app.on_event("startup")
async def on_startup():
    await tg_app.initialize()
    await tg_app.bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await tg_app.shutdown()

@app.post(WEBHOOK_URL)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, tg_app.bot) # Update.de_json is used to deserialize (convert from JSON) incoming Telegram update data into a usable telegram.Update object
    await tg_app.process_update(update)
    return {"ok": True}