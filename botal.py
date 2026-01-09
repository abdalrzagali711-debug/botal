import telebot
from telebot import types
import google.generativeai as genai
from flask import Flask
from threading import Thread
import os

# --- 1. إعداد الذكاء الاصطناعي (Gemini) ---
API_KEY = "AIzaSyBVbGGk_ircxLzq61ShCsHZN_CeKSGgP9s"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- 2. إعداد البوت (تأكد من وضع التوكن الخاص بك) ---
TOKEN = "8313424329:AAF4K5FgAM8rNJsUFMNSWUTWG1Mcwns-dro"
bot = telebot.TeleBot(TOKEN)

# --- 3. إعدادات الأدمن (لوحة التحكم) ---
# استبدل الرقم أدناه بالآيدي الخاص بك (الذي حصلت عليه من userinfobot)
ADMIN_ID = 5524416062  

USER_FILE = "users.txt"

def add_user(uid):
    if not os.path.exists(USER_FILE): open(USER_FILE, 'w').close()
    with open(USER_FILE, 'r') as f:
        users = f.read().splitlines()
    if str(uid) not in users:
        with open(USER_FILE, 'a') as f:
            f.write(str(uid) + "\n")

# --- 4. سيرفر Flask للبقاء حياً على Render ---
app = Flask('')
@app.route('/')
def home(): return "AI Bot is Online!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()

# --- 5. نظام الأزرار ---
def main_menu(uid):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_chat = types.KeyboardButton("💬 ابدأ الدردشة")
    markup.add(btn_chat)
    if uid == ADMIN_ID:
        btn_stats = types.KeyboardButton("📊 عدد المستخدمين")
        markup.add(btn_stats)
    return markup

# --- 6. الأوامر ومعالجة الرسائل ---
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    bot.send_message(message.chat.id, "🤖 أهلاً بك في بوت الذكاء الاصطناعي BotTech AI\n\nاسألني عن أي شيء وسأجيبك فوراً!", 
                     reply_markup=main_menu(message.from_user.id))

@bot.message_handler(func=lambda m: m.text == "📊 عدد المستخدمين")
def stats(message):
    if message.from_user.id == ADMIN_ID:
        if os.path.exists(USER_FILE):
            with open(USER_FILE, 'r') as f:
                count = len(f.read().splitlines())
            bot.send_message(message.chat.id, f"👥 إجمالي عدد مستخدمي البوت: {count}")
        else:
            bot.send_message(message.chat.id, "👥 عدد المستخدمين: 0")

@bot.message_handler(func=lambda m: m.text == "💬 ابدأ الدردشة")
def chat_start(message):
    bot.send_message(message.chat.id, "تفضل، أنا أسمعك.. اكتب سؤالك الآن!")

@bot.message_handler(func=lambda m: True)
def handle_ai(message):
    # تجاهل الأزرار
    if message.text in ["💬 ابدأ الدردشة", "📊 عدد المستخدمين"]: return
    
    thinking = bot.reply_to(message, "🤔 جاري التفكير...")
    try:
        response = model.generate_content(message.text)
        bot.edit_message_text(response.text, message.chat.id, thinking.message_id)
    except Exception as e:
        bot.edit_message_text("❌ عذراً، لم أستطع معالجة طلبك حالياً.", message.chat.id, thinking.message_id)

# --- 7. التشغيل ---
if __name__ == "__main__":
    keep_alive()
    bot.remove_webhook()
    print("AI Bot starting...")
    bot.infinity_polling(skip_pending=True)