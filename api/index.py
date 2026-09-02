import os
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Vercel se token uthana, environment variable ke zariye
TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is not set!")

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

REQUIRED_CHATS = ['@studenthelpclub', '@studenthelpclubofficial'] 
FINAL_GROUP_LINK = "https://t.me/+YwUmMpjCgHFkZDdl"

ASSIGNMENT_WEBSITE = "https://studenthelpclub.in" 
JOBS_WEBSITE = "https://jobs.studenthelpclub.in"
UTILITY_TOOLS = "https://shctools.in/"

# User states ko track karne ke liye temporary memory (enrollment input ke liye)
WAITING_FOR_ENROLLMENT = set()

def check_membership(user_id):
    """Checks if the user is present in all REQUIRED_CHATS."""
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
    """Generates the main menu markup with Check Result button."""
    markup = InlineKeyboardMarkup(row_width=1)
    btn_result = InlineKeyboardButton("🔍 Check IGNOU Result", callback_data="start_check_result")
    btn_group = InlineKeyboardButton("📚 IGNOU Solved Assignments", url=FINAL_GROUP_LINK)
    btn_website = InlineKeyboardButton("🌐 Assignment Website", url=ASSIGNMENT_WEBSITE)
    btn_jobs = InlineKeyboardButton("💼 Jobs Updates", url=JOBS_WEBSITE)
    btn_tools = InlineKeyboardButton("🛠️ Utility Tools", url=UTILITY_TOOLS)
    markup.add(btn_result, btn_group, btn_website, btn_jobs, btn_tools)
    return markup

def send_join_message(chat_id):
    """Sends the force join message with buttons."""
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
        chat_id, 
        join_msg, 
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.message_handler(commands=['start', 'restart'])
def send_welcome(message):
    user_id = message.from_user.id
    command = message.text.split()[0].lower() 
    
    if check_membership(user_id):
        if command == '/restart':
            welcome_text = "🔄 <b>Menu Restarted Successfully!</b>\n\n"
        else:
            welcome_text = "👋 <b>Welcome back to Student Help Club!</b>\n\n"
            
        welcome_text += (
            "Aap already verified member hain. 🎉\n\n"
            "👇 <i>Neeche diye gaye buttons se apni zaroorat ka option select karein:</i>"
        )
        bot.send_message(
            message.chat.id, 
            welcome_text, 
            parse_mode='HTML', 
            reply_markup=get_main_menu()
        )
    else:
        send_join_message(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_callback(call):
    user_id = call.from_user.id
    
    if check_membership(user_id):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass 
            
        success_msg = (
            "✅ <b>Verification Successful!</b>\n\n"
            "Dhanyawad! Ab aap Student Help Club ke verified member hain. 🎉\n\n"
            "👇 <i>Neeche diye gaye buttons se Result check karein, Assignment website, Jobs ya tools access karein:</i>"
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
            "❌ Kripya pehle upar diye gaye dono channels join karein!", 
            show_alert=False
        )

# Jab user "Check Result" button click karega
@bot.callback_query_handler(func=lambda call: call.data == "start_check_result")
def prompt_enrollment(call):
    user_id = call.from_user.id
    if not check_membership(user_id):
        bot.answer_callback_query(call.id, "❌ Kripya pehle channels join karein!", show_alert=True)
        send_join_message(call.message.chat.id)
        return
    
    WAITING_FOR_ENROLLMENT.add(user_id)
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "📝 <b>Apna Enrollment Number yahan type karke bhejein:</b>",
        parse_mode='HTML'
    )

def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except:
        return False

@bot.message_handler(func=lambda message: True, content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice', 'location', 'contact'])
def continuous_check(message):
    user_id = message.from_user.id
    chat_type = message.chat.type
    
    # 1. Agar user group me message kar raha hai (pdf restriction logic)
    if chat_type in ['group', 'supergroup']:
        if is_admin(message.chat.id, user_id):
            return
        
        if not check_membership(user_id):
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except Exception:
                pass
            return 
            
        if message.content_type == 'document':
            file_name = message.document.file_name.lower() if message.document.file_name else ""
            mime_type = message.document.mime_type if message.document.mime_type else ""
            if mime_type == 'application/pdf' or file_name.endswith('.pdf'):
                return 
                
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
            
    # 2. Agar user direct bot se baat kar raha hai (Private Chat)
    elif chat_type == 'private':
        if not check_membership(user_id):
             send_join_message(message.chat.id)
        else:
            if message.content_type == 'text' and not message.text.startswith('/'):
                # Check karo kya user ne Result ke liye enrollment number bheja hai?
                if user_id in WAITING_FOR_ENROLLMENT:
                    WAITING_FOR_ENROLLMENT.remove(user_id)
                    enr_number = message.text.strip()
                    
                    # Aapka manga gaya professional message
                    professional_msg = (
                        f"✅ <b>Enrollment Number ({enr_number}) received!</b>\n\n"
                        "⏳ Kuch der mein result isi chat mein aa jayega, "
                        "kripya channel koi leave na karein free assignment aur update ke liye."
                    )
                    bot.send_message(
                        message.chat.id, 
                        professional_msg, 
                        parse_mode='HTML', 
                        reply_markup=get_main_menu()
                    )
                else:
                     welcome_text = (
                        "Aap already verified member hain. 🎉\n\n"
                        "👇 <i>Neeche diye gaye buttons se apni zaroorat ka option select karein:</i>"
                    )
                     bot.send_message(
                        message.chat.id, 
                        welcome_text, 
                        parse_mode='HTML', 
                        reply_markup=get_main_menu()
                    )

# Vercel Flask Routes
@app.route('/', methods=['GET', 'POST'])
@app.route('/api/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Student Help Club Bot is alive and running 24/7!', 200
