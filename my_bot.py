import telebot
from telebot import types
import time
import os

# === 配置区域 ===
API_TOKEN = "8235876145:AAH9xfHaogajtOwzuV02iyfMNoRG2l2E4do"
ADMIN_IDS = [1840751528, 1280460690]
SUBSCRIBERS_FILE = "subscribers.txt"
BROADCAST_DELAY = 1.2  # 每1.2秒发一个，安全群发

bot = telebot.TeleBot(API_TOKEN)

# === 自动欢迎 + 图片 + 按钮 ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    first_name = message.from_user.first_name or "Boss"

    # 保存订阅者
    with open(SUBSCRIBERS_FILE, "a") as f:
        f.write(str(chat_id) + "\n")

    welcome_text = f"""👋 HI {first_name}！

🪜 Step 1:
Join Nanas44 Official Channel Claim Free 🎁

🪜 Step 2:
Join Grouplink IOI Partnership Ambil E-wallet Angpaw 💸
"""

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📢 NANAS44 OFFICIAL CHANNEL", url="https://t.me/nanas44")
    btn2 = types.InlineKeyboardButton("💸 E-WALLET ANGPAO GROUP", url="https://t.me/addlist/OyQ3Pns_j3w5Y2M1")
    markup.add(btn1)
    markup.add(btn2)

    # 发欢迎图片
    if os.path.exists("banner-01.png"):
        with open("banner-01.png", "rb") as photo:
            bot.send_photo(chat_id, photo)

    # 发文字和按钮
    bot.send_message(chat_id, welcome_text, reply_markup=markup)

# === 管理员广播指令 ===
@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ 你没有权限使用此功能。")
        return

    msg = bot.send_message(message.chat.id, "📢 请发送你要广播的内容：")
    bot.register_next_step_handler(msg, do_broadcast)

def do_broadcast(message):
    try:
        with open(SUBSCRIBERS_FILE, "r") as f:
            subscribers = list(set(f.read().splitlines()))

        count = 0
        for user_id in subscribers:
            try:
                bot.send_message(user_id, message.text)
                count += 1
                time.sleep(BROADCAST_DELAY)
            except:
                continue
        bot.reply_to(message, f"✅ 广播完成，已发送给 {count} 位用户。")
    except Exception as e:
        bot.reply_to(message, f"❌ 出错：{e}")

# === 查看订阅人数 ===
@bot.message_handler(commands=['subcount'])
def handle_subcount(message):
    if not os.path.exists(SUBSCRIBERS_FILE):
        bot.reply_to(message, "目前还没有任何订阅者。")
        return

    with open(SUBSCRIBERS_FILE, "r") as f:
        subscribers = set(f.read().splitlines())
    count = len(subscribers)
    bot.reply_to(message, f"目前共有 {count} 位订阅者 ✅")

# === 启动 Bot ===
print("🤖 Bot 已启动，等待消息中...")
bot.infinity_polling()
