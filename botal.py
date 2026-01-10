import telebot
from telebot import types
import google.generativeai as genai
from flask import Flask
from threading import Thread
import os

# 1. إعداد الذكاء الاصطناعي (تم استخدام مفتاحك الموضح في الصورة)
API_KEY = "AIzaSyBVbGGk_ircxLzq61ShCsHZN_CeKSGgP9s"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. إعداد البوت (تأكد من وضع التوكن الصحيح هنا)
TOKEN = 8313424329:AAF4K5FgAM8rNJsUFMNSWUTWG1Mcwns-dro"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 5524416062  # ضع الآيدي الخاص بك

# 3. سيرفر ويب خفيف جداً (لإرضاء Cron-job و Render)
app = Flask('')
@app.route('/')
def home(): 
    return "OK" # إرجاع كلمة واحدة فقط لمنع خطأ "بيانات كبيرة"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 4. معالجة الرسائل
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💬 ابدأ الدردشة")
    bot.send_message(message.chat.id, "🤖 البوت يعمل بنجاح الآن بالذكاء الاصطناعي!", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def ai_chat(message):
    if message.text == "💬 ابدأ الدردشة":
        bot.send_message(message.chat.id, "تفضل، اسألني أي شيء.")
        return
    
    # رسالة انتظار مؤقتة
    wait = bot.reply_to(message, "💬 جاري التفكير...")
    try:
        response = model.generate_content(message.text)
        bot.edit_message_text(response.text, message.chat.id, wait.message_id)
    except:
        bot.edit_message_text("❌ عذراً، المحرك مشغول حالياً. حاول ثانية.", message.chat.id, wait.message_id)

# 5. تشغيل السيرفر والبوت معاً
if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(skip_pending=True)).start()
    run()
