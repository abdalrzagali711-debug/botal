import telebot
from telebot import types
import google.generativeai as genai
from flask import Flask
from threading import Thread
import os

# --- 1. إعداد الذكاء الاصطناعي (Gemini) ---
# المفتاح الخاص بك
API_KEY = "AIzaSyBVbGGk_ircxLzq61ShCsHZN_CeKSGgP9s"
genai.configure(api_key=API_KEY)

# استخدام نموذج gemini-1.5-flash لأنه الأسرع والأكثر توافقاً حالياً
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. إعداد البوت ---
TOKEN = "8313424329:AAF4K5FgAM8rNJsUFMNSWUTWG1Mcwns-dro" 
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 5524416062 # ضع رقم الآيدي الخاص بك

USER_FILE = "users_list.txt"

def add_user(uid):
    if not os.path.exists(USER_FILE): open(USER_FILE, "w").close()
    with open(USER_FILE, "r") as f:
        if str(uid) not in f.read().splitlines():
            with open(USER_FILE, "a") as fa: fa.write(str(uid) + "\n")

# --- 3. سيرفر Flask (لحل مشكلة Render) ---
app = Flask('')
@app.route('/')
def home(): return "Botal AI is Live and Ready!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 4. معالجة الرسائل ---
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💬 ابدأ الدردشة")
    if message.from_user.id == ADMIN_ID: markup.add("📊 عدد المستخدمين")
    bot.send_message(message.chat.id, "🤖 أهلاً بك! تم تحديث النظام للنسخة الأحدث.\nأنا جاهز الآن للرد على استفساراتك.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📊 عدد المستخدمين")
def stats(message):
    if message.from_user.id == ADMIN_ID:
        with open(USER_FILE, "r") as f: count = len(f.read().splitlines())
        bot.send_message(message.chat.id, f"👥 عدد المستخدمين: {count}")

@bot.message_handler(func=lambda m: True)
def chat_logic(message):
    if message.text == "💬 ابدأ الدردشة":
        bot.send_message(message.chat.id, "تفضل، أنا أسمعك.. اسألني أي شيء!")
        return

    # رسالة انتظار أثناء معالجة الذكاء الاصطناعي
    wait_msg = bot.reply_to(message, "💬 جاري التفكير باستخدام Gemini 1.5...")
    try:
        # توليد المحتوى من الذكاء الاصطناعي
        response = model.generate_content(message.text)
        bot.edit_message_text(response.text, message.chat.id, wait_msg.message_id)
    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text("❌ عذراً، واجهت مشكلة في الاتصال بمحرك الذكاء الاصطناعي. يرجى المحاولة لاحقاً.", message.chat.id, wait_msg.message_id)

# --- 5. التشغيل المتوازي ---
if __name__ == "__main__":
    # تشغيل البوت في الخلفية
    Thread(target=lambda: bot.infinity_polling(skip_pending=True)).start()
    # تشغيل السيرفر الرئيسي
    run()
