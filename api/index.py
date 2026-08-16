import os
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '8738828553:AAH10YEMWy-QVaGGWssAK6JF3N8rwP4ShHs'
bot = telebot.TeleBot(TOKEN)
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
        bot.send_message(message.chat.id, f"Welcome back to Student Help Club! 🎉\nYahan aapka assignment group link hai: {FINAL_GROUP_LINK}")
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 Join Main Channel", url="https://t.me/studenthelpclub"))
        markup.add(InlineKeyboardButton("👥 Join Chat Group", url="https://t.me/studenthelpclubofficial"))
        markup.add(InlineKeyboardButton("✅ JOINED", callback_data="verify_join"))
        
        bot.send_message(
            message.chat.id, 
            "🔐 Bot use karne ke liye pehle hamare niche diye gaye dono channel/group ko join karein:", 
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_callback(call):
    user_id = call.from_user.id
    
    if check_membership(user_id):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            print("Message delete nahi ho paya:", e)
            
        bot.send_message(call.message.chat.id, f"Verification successful! ✅\nYe raha aapka Ignou Solved Assignment group: {FINAL_GROUP_LINK}")
    else:
        bot.answer_callback_query(call.id, "Aapne abhi tak sabhi channels join nahi kiye hain. Kripya dono ko join karein!", show_alert=True)

# Vercel Serverless Webhook Route (Simplified)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Student Help Club Bot is alive and running 24/7!', 200
