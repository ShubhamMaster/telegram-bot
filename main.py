import os
import json
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CommandHandler,
    ContextTypes, filters
)
from utils import fetch_erp_data

# === CONFIGURATION ===
# BOT_TOKEN = "7888406641:AAHPDqV_NpQdnSW26xb3wiPLR-D7_cp__Dg"
BOT_TOKEN = os.getenv("BOT_TOKEN")
ACCESS_CODE = "KKN"
ACCESS_TIMEOUT = timedelta(minutes=5)
LOGIN_DIR = "login"
os.makedirs(LOGIN_DIR, exist_ok=True)

# === USER DATA UTILS ===
def get_user_data(username):
    path = f"{LOGIN_DIR}/{username}_data.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            if "access_time" in data:
                data["access_time"] = datetime.fromisoformat(data["access_time"])
            return data
    return {"access_granted": False, "access_time": None}

def save_user_data(username, data):
    path = f"{LOGIN_DIR}/{username}_data.json"
    data_to_save = data.copy()
    data_to_save["access_time"] = data_to_save["access_time"].isoformat()
    with open(path, "w") as f:
        json.dump(data_to_save, f, indent=4)

# === /start COMMAND HANDLER ===
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or str(update.effective_user.id)
    user_data = get_user_data(username)
    now = datetime.now()

    access_granted = user_data.get("access_granted", False)
    access_time = user_data.get("access_time")

    if access_granted and access_time and now - access_time < ACCESS_TIMEOUT:
        await update.message.reply_text(
            "👋 Welcome back! ✅ You’re already logged in.\nJust send your *12-digit PRN* to fetch ERP data."
        )
    else:
        await update.message.reply_text(
            "👋 Welcome to the *ERP Info Bot!*\n\n🔐 Please enter your *access code* to begin."
        )

# === MESSAGE HANDLER (access code + PRN logic) ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    username = update.effective_user.username or str(update.effective_user.id)
    now = datetime.now()

    user_data = get_user_data(username)
    access_granted = user_data.get("access_granted", False)
    access_time = user_data.get("access_time")

    # Check expiration
    if access_time and now - access_time > ACCESS_TIMEOUT:
        access_granted = False
        user_data["access_granted"] = False

    # Require access code if not granted
    if not access_granted:
        if user_input.upper() == ACCESS_CODE:
            user_data["access_granted"] = True
            user_data["access_time"] = now
            save_user_data(username, user_data)

            try:
                await update.message.delete()
            except Exception as e:
                print("⚠️ Could not delete message:", e)

            await update.message.reply_text(
                "✅ Access granted!\nNow send your *12-digit PRN number* to get your ERP details."
            )
        else:
            await update.message.reply_text(
                "🔐 This service requires access.\nPlease enter a valid *access code* to continue."
            )
        return

    # Handle PRN input
    if not user_input.isdigit() or len(user_input) != 12:
        await update.message.reply_text("❌ Invalid PRN. Please enter a *12-digit* number.")
        return

    await update.message.reply_text("⏳ Fetching your ERP data, please wait...")

    result = fetch_erp_data(user_input)

    if "error" in result:
        await update.message.reply_text(result["error"])
        return

    with open(f"{user_input}_data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    message_lines = [f"📄 *{result.pop('PageTitle', 'ERP Page')}*"]
    warning = result.pop("warning", None)

    for key, value in result.items():
        message_lines.append(f"*{key}:* {value}")

    if warning:
        message_lines.append(f"\n⚠️ *Warning:* _{warning}_")

    final_message = "\n".join(message_lines)
    await update.message.reply_text(f"✅ *ERP Data:*\n\n{final_message}", parse_mode="Markdown")

# === BOT START ===
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
app.run_polling()
