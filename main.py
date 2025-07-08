import json
import datetime
import threading
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

TOKEN = 7408316421:AAFqxaB39EtKCepdAO-8X-4uJMna92OfecM"
bot = Bot(token=TOKEN)
app = Flask(__name__)

USERS_FILE = "users.json"
ADMIN_ID = 123456789
ASK_USERNAME, ASK_PASSWORD, ASK_WALLET = range(3)

REQUIRED_CHANNELS = [
    ("@channel1", "NODE-1"),
    ("@channel2", "NODE-2"),
    ("@channel3", "NODE-3")
]

DAILY_QUIZ_QUESTION = {
    "question": "Which command is used to find hidden ports in a system?\n\nA. Nmap\nB. SQLmap\nC. Hydra\nD. Nikto",
    "answer": "a"
}

REFERRAL_REWARD = 10
MIN_REFERRALS_FOR_WITHDRAW = 100

def load_json(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USERS_FILE)
    if user_id not in users:
        users[user_id] = {"referrals": 0, "wallet": ""}
        save_json(USERS_FILE, users)

    keyboard = [
        [InlineKeyboardButton(name, url=f"https://t.me/{channel[1:]}")] for channel, name in REQUIRED_CHANNELS
    ]
    keyboard.append([InlineKeyboardButton("✅ I Have Joined", callback_data="check_join")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🚨 ACCESS REQUIRED 🚨\n\n"
        "⚠️ Join All STAR NODES To Unlock The Bot Features!\n\n"
        "👨‍💻 Developer Node: @teamtoxic009",
        reply_markup=reply_markup
    )

# ✅ Join Check
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ ACCESS GRANTED! Use /register to begin.")

# /register
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send your wallet address using /wallet command like:\n\n/wallet your_address")

# /wallet
async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USERS_FILE)

    if len(context.args) == 0:
        await update.message.reply_text("❌ Usage: /wallet your_address")
        return

    address = context.args[0]
    if user_id in users:
        users[user_id]["wallet"] = address
        save_json(USERS_FILE, users)
        await update.message.reply_text("✅ Wallet address saved!")
    else:
        await update.message.reply_text("❌ Please use /start first.")

# /refer
async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USERS_FILE)
    if user_id not in users:
        await update.message.reply_text("Use /start first.")
        return

    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    referrals = users[user_id].get("referrals", 0)

    await update.message.reply_text(
        f"👥 Invite your friends using this link:\n{referral_link}\n\n"
        f"💰 Current referrals: {referrals}"
    )

# /quiz
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = DAILY_QUIZ_QUESTION["question"]
    await update.message.reply_text(f"🧠 DAILY QUIZ 🧠\n\n{question}\n\nReply with the correct option (A, B, C, or D)")

# /withdraw
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USERS_FILE)
    user = users.get(user_id, {})

    if user.get("referrals", 0) < MIN_REFERRALS_FOR_WITHDRAW:
        await update.message.reply_text("❌ You need at least 100 referrals to withdraw.")
        return

    wallet = user.get("wallet", "")
    if not wallet:
        await update.message.reply_text("❌ No wallet address found. Set it using /wallet command.")
        return

    await update.message.reply_text(f"✅ Withdraw request received for wallet: {wallet}\nYour balance will be processed soon!")

# Message handler (quiz answer)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower().strip()
    if msg in ["a", "b", "c", "d"]:
        if msg == DAILY_QUIZ_QUESTION["answer"]:
            await update.message.reply_text("✅ Correct Answer!")
        else:
            await update.message.reply_text("❌ Wrong Answer!")

# ✅ Flask
@app.route('/')
def home():
    return "Star Bot is Running!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return 'ok'

def start_flask():
    app.run(host='0.0.0.0', port=8080)

# ✅ Init Bot
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
application.add_handler(CommandHandler("register", register))
application.add_handler(CommandHandler("wallet", wallet))
application.add_handler(CommandHandler("refer", refer))
application.add_handler(CommandHandler("quiz", quiz))
application.add_handler(CommandHandler("withdraw", withdraw))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == '__main__':
    threading.Thread(target=start_flask).start()
    application.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path=TOKEN,
        webhook_url=f"https://your-render-url.onrender.com/{TOKEN}"
  )
