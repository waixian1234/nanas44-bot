
import logging
import os
import datetime
import schedule
import time
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = '8235876145:AAH9xfHaogajtOwzuV02iyfMNoRG2l2E4do'
ADMIN_IDS = [1840751528, 1280460690]
application = None  # will be set later

SUBSCRIBER_FILE = "subscribers.txt"
LOG_DIR = "logs"
DELAY = 1.1  # seconds


def save_log(filename, data):
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(os.path.join(LOG_DIR, filename), "a") as f:
        f.write(data + "\n")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    first_name = update.effective_user.first_name or "there"
    # Save subscriber
    if not os.path.exists(SUBSCRIBER_FILE):
        open(SUBSCRIBER_FILE, "w").close()
    with open(SUBSCRIBER_FILE, "r+") as f:
        lines = f.read().splitlines()
        if user_id not in lines:
            f.write(f"{user_id}\n")
            save_log("new_users.txt", f"{datetime.datetime.now()} - {user_id}")
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


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("Please provide a message. Usage: /broadcast your message here")
        return
    with open(SUBSCRIBER_FILE, "r") as f:
        ids = list(set(f.read().splitlines()))
    success = 0
    for uid in ids:
        try:
            await context.bot.send_message(chat_id=int(uid), text=message)
            success += 1
            time.sleep(DELAY)
        except:
            continue
    await update.message.reply_text(f"Broadcast sent to {success} users.")


async def broadcast_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS or not update.message.photo:
        return
    caption = update.message.caption or ""
    with open(SUBSCRIBER_FILE, "r") as f:
        ids = list(set(f.read().splitlines()))
    success = 0
    file_id = update.message.photo[-1].file_id
    for uid in ids:
        try:
            await context.bot.send_photo(chat_id=int(uid), photo=file_id, caption=caption)
            success += 1
            time.sleep(DELAY)
        except:
            continue
    await update.message.reply_text(f"Photo broadcast sent to {success} users.")


async def forward_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    with open(SUBSCRIBER_FILE, "r") as f:
        ids = list(set(f.read().splitlines()))
    for uid in ids:
        try:
            await update.message.copy(chat_id=int(uid))
            time.sleep(DELAY)
        except:
            continue


async def subcount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    with open(SUBSCRIBER_FILE, "r") as f:
        ids = set(f.read().splitlines())
    await update.message.reply_text(f"👥 Total subscribers: {len(ids)}")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    text = """🧠 Bot Commands:
  /start - Welcome page
  /broadcast <text> - Send message to all
  (Send image+text directly to broadcast image)
  /subcount - Subscriber count
  /remove <id> - Remove user
  /restart - Restart bot
  /stats - Subscriber stats
  /bancheck - Check blocked users
  /activeusers - Show recent active users
  /export - Send subscriber list"""
    await update.message.reply_text(text)


async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not context.args:
        await update.message.reply_text("Usage: /remove <user_id>")
        return
    uid = context.args[0]
    with open(SUBSCRIBER_FILE, "r") as f:
        lines = f.read().splitlines()
    lines = [i for i in lines if i != uid]
    with open(SUBSCRIBER_FILE, "w") as f:
        f.write("\n".join(lines))
    await update.message.reply_text(f"Removed user: {uid}")


async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    with open(SUBSCRIBER_FILE, "rb") as f:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=f)


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMIN_IDS:
        await update.message.reply_text("Bot restarting...")
        os._exit(1)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    today = datetime.date.today().strftime("%Y-%m-%d")
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    today_count = 0
    yest_count = 0
    with open(os.path.join(LOG_DIR, "new_users.txt"), "r") as f:
        for line in f:
            if today in line:
                today_count += 1
            if yesterday in line:
                yest_count += 1
    with open(SUBSCRIBER_FILE, "r") as f:
        total = len(set(f.read().splitlines()))
    await update.message.reply_text(f"📊 Total: {total}\n📈 Today: {today_count}\n📉 Yesterday: {yest_count}")


async def bancheck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    banned = []
    with open(SUBSCRIBER_FILE, "r") as f:
        for uid in set(f.read().splitlines()):
            try:
                await context.bot.send_chat_action(chat_id=int(uid), action="typing")
                time.sleep(DELAY)
            except:
                banned.append(uid)
    await update.message.reply_text(f"❌ Blocked: {len(banned)} users")


async def activeusers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    log_path = os.path.join(LOG_DIR, "new_users.txt")
    count = 0
    with open(log_path, "r") as f:
        for line in f:
            if str(datetime.date.today() - datetime.timedelta(days=3)) in line:
                count += 1
    await update.message.reply_text(f"✅ Active users (last 3 days): {count}")


def backup_task():
    try:
        with open(SUBSCRIBER_FILE, "rb") as f:
            for admin_id in ADMIN_IDS:
                application.bot.send_document(chat_id=admin_id, document=f)
    except Exception as e:
        print("Backup error:", e)


def schedule_loop():
    schedule.every().day.at("00:00").do(backup_task)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("subcount", subcount))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("remove", remove_user))
    application.add_handler(CommandHandler("export", export))
    application.add_handler(CommandHandler("restart", restart))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("bancheck", bancheck))
    application.add_handler(CommandHandler("activeusers", activeusers))
    application.add_handler(MessageHandler(filters.PHOTO, broadcast_photo))
    application.add_handler(MessageHandler(filters.FORWARDED, forward_broadcast))

    threading.Thread(target=schedule_loop, daemon=True).start()
    application.run_polling()
