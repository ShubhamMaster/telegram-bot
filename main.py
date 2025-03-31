import os
import json
import random
import re
from telethon import TelegramClient, events
import google.generativeai as genai

# Load API credentials from environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Google Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-1.5-pro"
model = genai.GenerativeModel(MODEL_NAME)

# Initialize Telegram Bot
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage)
async def handle_message(event):
    await event.respond("Hello! Your bot is working on Railway!")

print("Bot is running...")
bot.run_until_disconnected()
