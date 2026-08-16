import os
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Aapka Bot Token (image_d78df8.png se)
TOKEN = '8738828553:AAEhJWrWNIPCUbPdi9-OQ13Jf4twNDUwuP4'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Yahan apne Student Help Club channel aur group ka username daalein (Bina link ke, bas @username)
REQUIRED_CHATS = ['@your_channel_username', '@your_group_username'] 
# Join karne ke baad jo main group ya link dena hai
FINAL_GROUP_LINK = "https://t.me/your_secret_group_link"

def check_membership(user_id):
    """Check karta hai ki user sabhi required chats mein hai ya nahi."""
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
        # Agar already joined hai
        bot.send_message(message.chat.id, f"Welcome back to Student Help Club! 🎉\nYahan aapka group link hai: {FINAL_GROUP_LINK}")
    else:
        # Agar joined nahi hai toh buttons bhejo
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 Join Channel 1", url="https://t.me/your_channel_username"))
        markup.add(InlineKeyboardButton("👥 Join Group", url="https://t.me/your_group_username"))
        markup.add(InlineKeyboardButton("✅ JOINED", callback_data="verify_join"))
        
        bot.send_message(
            message.chat.id, 
            "🔐 Bot use karne ke liye pehle hamare following channels/group ko join karein:", 
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_callback(call):
    user_id = call.from_user.id
    
    if check_membership(user_id):
        # 1. Join wala message delete karein
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            print("Message delete nahi ho paya:", e)
            
        # 2. Final link bhej dein
        bot.send_message(call.message.chat.id, f"Verification successful! ✅\nYe raha aapka main group: {FINAL_GROUP_LINK}")
    else:
        # Pop-up alert agar join nahi kiya hai
        bot.answer_callback_query(call.id, "Aapne abhi tak sabhi channels join nahi kiye hain. Kripya pehle join karein!", show_alert=True)

# Vercel Webhook Setup
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['POST', 'GET'])
def webhook(path):
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '!', 200
    return 'Student Help Club Bot is alive and running on Vercel!', 200