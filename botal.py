import telebot
from telebot import types
import google.generativeai as genai
from flask import Flask
from threading import Thread
import os

# --- 1. إعداد الذكاء الاصطناعي (Gemini) ---
# المفتاح الذي استخرجته أنت سابقاً
API_KEY = "AIzaSyBVbGGk_ircxLzq61ShCsHZN_CeKSGgP9s"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- 2. إعداد البوت ---
# ضع هنا التوكن الجديد الذي حصلت عليه من BotFather
TOKEN = "8313424329:AAF4K5FgAM8rNJsUFMNSWUTWG1Mcwns-dro"
bot = telebot.TeleBot(TOKEN)

# ضع هنا رقم الآيدي الخاص بك (ID) ليظهر لك زر التحكم
ADMIN_ID = 5524416062 

# ملف لتخزين آيدي المستخدمين
USER_FILE = "users_list.txt"

def add_to_db(uid):
    if not os.path.exists(USER_FILE): open(USER_FILE, 'w').close()
    with open(USER_FILE, 'r') as f:
        users = f.read().splitlines()
    if str(uid) not in users:
        with open(USER_FILE, 'a') as f:
            f.write(str(uid) + "\n")

# --- 3. سيرفر Flask (رابط الحياة لـ Render) ---
app = Flask('')

@app.route('/')
def home():
    return "AI Bot (botal.py) is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask, daemon=True)
    t.start()

# --- 4. الأزرار ---
def get_keyboard(uid):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("💬 ابدأ الدردشة"))
    if uid == ADMIN_ID:
        markup.add(types.KeyboardButton("📊 عدد المستخدمين"))
    return markup

# --- 5. استقبال الرسائل ---
@bot.message_handler(commands=['start'])
def welcome(message):
    add_to_db(message.from_user.id)
    bot.send_message(
        message.chat.id, 
        "🤖 أهلاً بك في بوت الذكاء الاصطناعي الحديث!\nاسألني أي سؤال وسأجيبك فوراً.",
        reply_markup=get_keyboard(message.from_user.id)
    )

@bot.message_handler(func=lambda m: m.text == "📊 عدد المستخدمين")
def show_users(message):
    if message.from_user.id == ADMIN_ID:
        if os.path.exists(USER_FILE):
            with open(USER_FILE, 'r') as f:
                count = len(f.read().splitlines())
            bot.send_message(message.chat.id, f"👥 عدد مستخدمي البوت الحالي: {count}")

@bot.message_handler(func=lambda m: m.text == "💬 ابدأ الدردشة")
def chat_info(message):
    bot.send_message(message.chat.id, "أنا أسمعك الآن، أرسل أي نص وسأرد عليك باستخدام الذكاء الاصطناعي.")

@bot.message_handler(func=lambda message: True)
def ai_logic(message):
    # لا ترد بالذكاء الاصطناعي إذا ضغط المستخدم على الأزرار
    if message.text in ["💬 ابدأ الدردشة", "📊 عدد المستخدمين"]:
        return

    thinking_msg = bot.reply_to(message, "💬 جاري التفكير...")
    try:
        response = model.generate_content(message.text)
        bot.edit_message_text(response.text, message.chat.id, thinking_msg.message_id)
    except Exception as e:
        bot.edit_message_text("⚠️ عذراً، واجهت مشكلة في معالجة طلبك.", message.chat.id, thinking_msg.message_id)

# --- 6. التشغيل النهائي ---
if __name__ == "__main__":
    keep_alive() # تشغيل السيرفر في الخلفية
    bot.remove_webhook() # تنظيف الاتصالات القديمة لتجنب خطأ 409
    print("Bot is starting via botal.py...")
    bot.infinity_polling(skip_pending=True)
