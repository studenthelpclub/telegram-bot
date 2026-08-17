import os
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Token direct likhne ke bajaye os.getenv ka use karein
TOKEN = os.getenv("8738828553:AAE-bUM0YJ02FvGiA6qjAyfIg1QD6cly2v8")
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
    
    for i in range(message.message_id, message.message_id - 6, -1):
        try:
            bot.delete_message(message.chat.id, i)
        except Exception:
            pass 

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
        # Professional & Clean Notification (show_alert=False kiya gaya hai taaki pop-up box na aaye)
        bot.answer_callback_query(
            call.id, 
            "❌ Kripya pehle upar diye gaye dono channels join karein!", 
            show_alert=False
        )

def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except:
        return False

@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'], content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice', 'location', 'contact'])
def restrict_to_pdf(message):
    if is_admin(message.chat.id, message.from_user.id):
        return
    
    if message.content_type == 'document':
        file_name = message.document.file_name.lower() if message.document.file_name else ""
        mime_type = message.document.mime_type if message.document.mime_type else ""
        
        if mime_type == 'application/pdf' or file_name.endswith('.pdf'):
            return 
            
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        pass

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Student Help Club Bot is alive and running 24/7!', 200
