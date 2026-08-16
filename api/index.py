import os
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '8738828553:AAH10YEMWy-QVaGGWssAK6JF3N8rwP4ShHs'
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

REQUIRED_CHATS = ['@studenthelpclub', '@studenthelpclubofficial'] 
FINAL_GROUP_LINK = "https://t.me/+YwUmMpjCgHFkZDdl"

def check_membership(user_id):
    for chat_id in REQUIRED_CHATS:
        try:
            member = bot.get_chat_member(chat_id, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            print(f"Error checking {chat_id}: {e}")
            return False
    return True

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if check_membership(user_id):
        # Agar pehle se joined hai toh professional welcome back message
        welcome_back = (
            "👋 <b>Welcome back to Student Help Club!</b>\n\n"
            "Aap already hamare verified member hain. 🎉\n\n"
            "📁 <b>Aapke IGNOU Solved Assignments yahan hain:</b>\n"
            f"👉 {FINAL_GROUP_LINK}"
        )
        bot.send_message(message.chat.id, welcome_back, parse_mode='HTML')
    else:
        # Professional Join Message
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 Join Main Channel", url="https://t.me/studenthelpclub"))
        markup.add(InlineKeyboardButton("👥 Join Chat Group", url="https://t.me/studenthelpclubofficial"))
        markup.add(InlineKeyboardButton("✅ JOINED", callback_data="verify_join"))
        
        join_msg = (
            "👋 <b>Welcome to Student Help Club Bot!</b>\n\n"
            "📚 IGNOU ke free solved assignments aur latest updates access karne ke liye, "
            "kripya hamare official channels ko join karein.\n\n"
            "👇 <i>Neeche diye gaye buttons par click karein aur join karne ke baad '✅ JOINED' dabayein.</i>"
        )
        
        bot.send_message(
            message.chat.id, 
            join_msg, 
            reply_markup=markup,
            parse_mode='HTML'
        )

@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_callback(call):
    user_id = call.from_user.id
    
    if check_membership(user_id):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            pass # Error print karne ki zaroorat nahi
            
        # Professional Success Message
        success_msg = (
            "✅ <b>Verification Successful!</b>\n\n"
            "Dhanyawad! Ab aap Student Help Club ke verified member hain. 🎉\n\n"
            "📁 <b>Aapka IGNOU Solved Assignment Group link:</b>\n"
            f"👉 {FINAL_GROUP_LINK}\n\n"
            "<i>Is link par click karke apna private group join karein.</i>"
        )
        bot.send_message(call.message.chat.id, success_msg, parse_mode='HTML')
    else:
        # Professional Alert Pop-up
        bot.answer_callback_query(
            call.id, 
            "⚠️ Alert: Aapne abhi tak dono channels join nahi kiye hain. Kripya pehle join karein aur phir verify karein.", 
            show_alert=True
        )

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Student Help Club Bot is alive and running 24/7!', 200
