import telebot
from telebot import types
import os

# === 替换成你自己的 Bot Token ===
bot = telebot.TeleBot("8235876145:AAH9xfHaogajtOwzuV02iyfMNoRG2l2E4do")

# === /start 欢迎函数 ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    first_name = message.from_user.first_name

    welcome_text = f"""👋 HI {first_name}！

🪜 Step 1:
Join Nanas44 Official Channel Claim Free 🎁

🪜 Step 2:
Join Grouplink IOI Partnership Ambil E-wallet Angpaw 💸
"""

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📡 NANAS44 OFFICIAL CHANNEL", url="https://t.me/nanas44")
    btn2 = types.InlineKeyboardButton("💸 E-WALLET ANGPAO GROUP", url="https://t.me/addlist/OyQ3Pns_j3w5Y2M1")
    markup.add(btn1)
    markup.add(btn2)

    # === 发送欢迎图片 ===
    image_path = os.path.join(os.path.dirname(__file__), "banner-01.png")
    if os.path.exists(image_path):
        with open(image_path, "rb") as photo:
            bot.send_photo(chat_id, photo)

    # === 发送欢迎文字 + 按钮 ===
    bot.send_message(chat_id, welcome_text, reply_markup=markup)

# === 群发广播函数 ===
@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    admin_ids = [1840751528, 1280460690]  # 你的管理员 ID
    if message.from_user.id not in admin_ids:
        return

    try:
        with open("subscribers.txt", "r") as f:
            subscribers = f.read().splitlines()
    except FileNotFoundError:
        subscribers = []

    for user_id in subscribers:
        try:
            bot.forward_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id + 1)
        except Exception as e:
            print(f"无法转发给 {user_id}: {e}")

# === 自动记录订阅者 ===
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    user_id = str(message.chat.id)
    try:
        with open("subscribers.txt", "r") as f:
            subscribers = f.read().splitlines()
    except FileNotFoundError:
        subscribers = []

    if user_id not in subscribers:
        subscribers.append(user_id)
        with open("subscribers.txt", "a") as f:
            f.write(user_id + "\n")

# === 启动 Bot ===
bot.polling()
