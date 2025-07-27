
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import datetime
import schedule
import time
import threading

TOKEN = '8235876145:AAH9xfHaogajtOwzuV02iyfMNoRG2l2E4do'
ADMIN_IDS = [1840751528, 1280460690]
application = None  # will be set later

# ========== 功能 1：欢迎页 ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.effective_user.first_name or "there"
    user_id = update.effective_user.id

    # Save subscriber
    with open("subscribers.txt", "a") as f:
        if str(user_id) not in open("subscribers.txt").read():
            f.write(f"{user_id}\n")

    # Welcome text
    welcome_text = f"""👋 HI {first_name}！

🪜 Step 1:
Join Nanas44 Official Channel Claim Free 🎁

🪜 Step 2:
Join Grouplink IOI Partnership Ambil E-wallet Angpaw 💸"""

    keyboard = [
        [InlineKeyboardButton("NANAS44 OFFICIAL CHANNEL", url="https://t.me/nanas44")],
        [InlineKeyboardButton("E-WALLET ANGPAO GROUP", url="https://t.me/addlist/OyQ3Pns_j3w5Y2M1")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open("banner-01.png", "rb") as img:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=img, caption=welcome_text, reply_markup=reply_markup)

# ========== 功能 2：/broadcast ==========
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Unauthorized.")
        return

    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("Please provide a message. Usage: /broadcast Your text here")
        return

    with open("subscribers.txt", "r") as f:
        subscribers = f.read().splitlines()

    success = 0
    for user_id in subscribers:
        try:
            await context.bot.send_message(chat_id=int(user_id), text=message)
            success += 1
        except:
            continue
    await update.message.reply_text(f"Broadcast sent to {success} users.")

# ========== 功能 3：自动接收转发并群发 ==========
async def forward_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    with open("subscribers.txt", "r") as f:
        subscribers = f.read().splitlines()

    for user_id in subscribers:
        try:
            await update.message.copy(chat_id=int(user_id))
        except:
            continue

# ========== 功能 4：每天定时发 subscribers.txt ==========
def backup_task():
    try:
        with open("subscribers.txt", "rb") as f:
            for admin_id in ADMIN_IDS:
                application.bot.send_document(chat_id=admin_id, document=f)
    except Exception as e:
        print("Backup error:", e)

def schedule_loop():
    schedule.every().day.at("00:00").do(backup_task)
    while True:
        schedule.run_pending()
        time.sleep(1)

# ========== 主程序 ==========
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(MessageHandler(filters.FORWARDED, forward_broadcast))

    threading.Thread(target=schedule_loop, daemon=True).start()
    application.run_polling()
