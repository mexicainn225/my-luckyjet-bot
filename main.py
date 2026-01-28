import telebot
import random
from datetime import datetime, timedelta
from flask import Flask
import threading
import os
import time

# --- 1. CONFIGURATION ---
app = Flask(__name__)

ADMIN_ID = 5724620019  
API_TOKEN = '8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0'
bot = telebot.TeleBot(API_TOKEN)

CANAL_ID = "@mexicain225officiel" 
LIEN_INSCRIPTION = "https://lkbb.cc/e2d8"
CODE_PROMO = "COK225"
CONTACT_ADMIN = "@MEXICAINN225"
ID_VIDEO_UNIQUE = "https://t.me/gagnantpro1xbet/138958" 

user_signals_count = {}
registered_users = set()
premium_signals_today = 0
last_reset_date = datetime.now().date()

@app.route('/')
def health_check():
    return "Bot Mexicain Operational", 200

def check_sub(user_id):
    if user_id == ADMIN_ID: return True
    try:
        member = bot.get_chat_member(CANAL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        telebot.types.KeyboardButton("🚀 OBTENIR UN SIGNAL"),
        telebot.types.KeyboardButton("👑 SIGNAL PREMIUM (VIP) 👑")
    )
    return markup

# --- 2. STATS ADMIN ---
@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id == ADMIN_ID:
        msg = (f"📊 **STATISTIQUES ADMIN**\n\n"
               f"👥 Utilisateurs : {len(registered_users)}\n"
               f"💎 Premium émis : {premium_signals_today}/20")
        bot.send_message(message.chat.id, msg, parse_mode='Markdown')

# --- 3. GESTION DES COMMANDES ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    registered_users.add(user_id)
    if not check_sub(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 Rejoindre le Canal", url="https://t.me/mexicain225officiel"))
        bot.send_message(message.chat.id, "👋 **ACCÈS PRIVÉ**\nRejoins le canal pour activer le bot.", reply_markup=markup)
        return
    bot.send_message(message.chat.id, "✅ **ACCÈS VALIDÉ**", reply_markup=main_menu())

# --- 4. LOGIQUE DES SIGNAUX ---

@bot.message_handler(func=lambda message: message.text in ["🚀 OBTENIR UN SIGNAL", "👑 SIGNAL PREMIUM (VIP) 👑"])
def handle_signals(message):
    global premium_signals_today, last_reset_date
    user_id = message.from_user.id
    
    if not check_sub(user_id):
        bot.reply_to(message, "❌ Abonne-toi au canal !")
        return

    # Limite gratuite de 3 signaux
    count = user_signals_count.get(user_id, 0)
    
    if user_id != ADMIN_ID and count >= 3:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🎁 S'INSCRIRE (DÉBLOQUER TOUT)", url=LIEN_INSCRIPTION))
        bot.send_message(message.chat.id, 
            "🔒 **LIMITE ATTEINTE !**\n\n"
            "Pour accéder aux signaux illimités et au Premium :\n"
            f"1️⃣ Inscris-toi avec le code : **{CODE_PROMO}**\n"
            "2️⃣ Fais un dépôt pour activer ton compte.\n\n"
            "Une fois inscrit, tout est débloqué à vie ! ✅", 
            reply_markup=markup, parse_mode='Markdown')
        return

    # Temps pour tous les signaux
    now = datetime.now()
    wait = random.randint(3, 6)
    time_range = f"{(now + timedelta(minutes=wait)).strftime('%H:%M')} - {(now + timedelta(minutes=wait+2)).strftime('%H:%M')}"

    # --- MODE PREMIUM ---
    if message.text == "👑 SIGNAL PREMIUM (VIP) 👑":
        if datetime.now().date() > last_reset_date:
            premium_signals_today = 0
            last_reset_date = datetime.now().date()
            
        if premium_signals_today >= 20:
            bot.send_message(message.chat.id, "🚫 **LIMITE VIP DU JOUR ATTEINTE (20/20)**")
            return
        
        premium_signals_today += 1
        côte_vip = round(random.uniform(10.00, 300.00), 2)
        
        texte_premium = (
            f"🔱 SIGNAL VIP PREMIUM 🔱\n"
            f"━━━━━━━━━━━━━━━━━━\n"
f"⚡️ TIME : {time_range}\n"
            f"💰 PRÉVISION : {côte_vip}X+\n"
            f"📉 RESTANTS : {20 - premium_signals_today}/20\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎁 CODE : **{CODE_PROMO}**"
        )
        markup_p = telebot.types.InlineKeyboardMarkup()
        markup_p.add(telebot.types.InlineKeyboardButton("📲 JOUER VIP", url=LIEN_INSCRIPTION))
        
        bot.send_video(message.chat.id, ID_VIDEO_UNIQUE, caption=texte_premium, reply_markup=markup_p, parse_mode='Markdown')
        return

    # --- MODE NORMAL ---
    user_signals_count[user_id] = count + 1
    cote = random.randint(3, 60)
    prev = random.randint(10, 45)
    assu = random.randint(2, 8)

    texte_normal = (
        f"🚀 SIGNAL MEXICAIN225 🧨\n\n"
        f"⚡️ TIME : {time_range}\n"
        f"⚡️ CÔTE : {cote}X+\n"
        f"⚡️ PRÉVISION : {prev}X+\n"
        f"⚡️ ASSURANCE : {assu}X+\n\n"
        f"📍 [CLIQUE ICI POUR JOUER]({LIEN_INSCRIPTION})\n"
        f"🎁 CODE PROMO : **{CODE_PROMO}**\n\n"
        f"👤 CONTACT : {CONTACT_ADMIN}"
    )
    
    markup_n = telebot.types.InlineKeyboardMarkup()
    markup_n.add(telebot.types.InlineKeyboardButton("📲 JOUER MAINTENANT", url=LIEN_INSCRIPTION))

    bot.send_video(message.chat.id, ID_VIDEO_UNIQUE, caption=texte_normal, reply_markup=markup_n, parse_mode='Markdown')

# --- 5. LANCEMENT ---
if __name__== "__main__":
    bot.remove_webhook()
    time.sleep(2)
    threading.Thread(target=bot.infinity_polling, kwargs={'timeout': 60}, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
