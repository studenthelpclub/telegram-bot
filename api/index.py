import os
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '8738828553:AAH10YEMWy-QVaGGWssAK6JF3N8rwP4ShHs'
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

REQUIRED_CHATS = ['@studenthelpclub', '@studenthelpclubofficial'] 
FINAL_GROUP_LINK = "https://t.me/+YwUmMpjCgHFkZDdl"

ASSIGNMENT_WEBSITE = "https://studenthelpclub.in" 
JOBS_WEBSITE = "https://jobs.studenthelpclub.in"
UTILITY_TOOLS = "https://shctools.in/"

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

def get_main_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    btn_group = InlineKeyboardButton("📚 IGNOU Solved Assignments", url=FINAL_GROUP_LINK)
    btn_website = InlineKeyboardButton("🌐 Assignment Website", url=ASSIGNMENT_WEBSITE)
    btn_jobs = InlineKeyboardButton("💼 Jobs Updates", url=JOBS_WEBSITE)
    btn_tools = InlineKeyboardButton("🛠️ Utility Tools", url=UTILITY_TOOLS)
    
    markup.add(btn_group, btn_website, btn_jobs, btn_tools)
    return markup

@bot.message_handler(commands=['start', 'restart'])
def send_welcome(message):
    user_id = message.from_user.id
    command = message.text.split()[0].lower() 
    
    # 🧹 SMART CHAT CLEANER: Ye current command aur pichle kuch messages ko dhundh kar delete karega
    # Range 6 ka matlab hai: current message aur usse pehle ke 5 messages clean karega
    for i in range(message.message_id, message.message_id - 6, -1):
        try:
            bot.delete_message(message.chat.id, i)
        except Exception:
            pass # Agar koi message pehle se delete ho chuka hai, toh error ignore karega

    if check_membership(user_id):
        if command == '/restart':
            welcome_back = (
                "🔄 <b>Menu Restarted Successfully!</b>\n\n"
                "Aap already verified member hain. 🎉\n\n"
                "👇 <i>Neeche diye gaye buttons se apni zaroorat ka option select karein:</i>"
            )
        else:
            welcome_back = (
                "👋 <b>Welcome back to Student Help Club!</b>\n\n"
                "Aap already verified member hain. 🎉\n\n"
                "👇 <i>Neeche diye gaye buttons se apni zaroorat ka option select karein:</i>"
            )
            
        bot.send_message(
            message.chat.id, 
            welcome_back, 
            parse_mode='HTML', 
            reply_markup=get_main_menu()
        )
    else:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("📢 Join Main Channel", url="https://t.me/studenthelpclub"))
        markup.add(InlineKeyboardButton("👥 Join Chat Group", url="https://t.me/studenthelpclubofficial"))
        markup.add(InlineKeyboardButton("✅ JOINED", callback_data="verify_join"))
        
        join_msg = (
            "👋 <b>Welcome to Student Help Club Bot!</b>\n\n"
            "📚 IGNOU ke free solved assignments, jobs aur latest updates access karne ke liye, "
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
            # JOINED button dabane par wo purana verify wala message delete ho jayega
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            pass 
            
        success_msg = (
            "✅ <b>Verification Successful!</b>\n\n"
            "Dhanyawad! Ab aap Student Help Club ke verified member hain. 🎉\n\n"
            "👇 <i>Neeche diye gaye buttons se Assignment website, Jobs, Tools ya secret group access karein:</i>"
        )
        bot.send_message(
            call.message.chat.id, 
            success_msg, 
            parse_mode='HTML',
            reply_markup=get_main_menu()
        )
    else:
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
