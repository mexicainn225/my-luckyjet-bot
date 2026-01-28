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

# --- REMPLACE PAR TON FILE_ID DE VIDÉO ---
ID_VIDEO_UNIQUE = "TON_FILE_ID_ICI" 

# Stockage des données
user_signals_count = {}
registered_users = set()
premium_signals_today = 0
last_reset_date = datetime.now().date()

@app.route('/')
def health_check():
    return "Bot is alive!", 200

def check_sub(user_id):
    if user_id == ADMIN_ID: return True
    try:
        member = bot.get_chat_member(CANAL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = telebot.types.KeyboardButton("🚀 OBTENIR UN SIGNAL")
    btn2 = telebot.types.KeyboardButton("👑 SIGNAL PREMIUM (VIP) 👑")
    markup.add(btn1, btn2)
    return markup

# --- 2. GESTION DES COMMANDES ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    registered_users.add(user_id)
    if not check_sub(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 Rejoindre le Canal", url="https://t.me/mexicain225officiel"))
        bot.send_message(message.chat.id, "👋 **ACCÈS RESTREINT**\n\nRejoins le canal pour activer tes signaux !", reply_markup=markup, parse_mode='Markdown')
        return
    bot.send_message(message.chat.id, "✅ **ACCÈS VALIDÉ**\n\nChoisis ton mode de jeu :", reply_markup=main_menu(), parse_mode='Markdown')

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, f"📊 **STATISTIQUES**\n\n👥 Utilisateurs : {len(registered_users)}\n💎 Signaux Premium : {premium_signals_today}/20")

# --- 3. LOGIQUE DES SIGNAUX ---

@bot.message_handler(func=lambda message: message.text in ["🚀 OBTENIR UN SIGNAL", "👑 SIGNAL PREMIUM (VIP) 👑"])
def handle_signals(message):
    global premium_signals_today, last_reset_date
    user_id = message.from_user.id
    
    if not check_sub(user_id):
        bot.reply_to(message, "❌ Abonne-toi au canal !")
        return

    # Reset journalier
    if datetime.now().date() > last_reset_date:
        premium_signals_today = 0
        last_reset_date = datetime.now().date()

    # --- MODE PREMIUM (Côtes 10x à 300x) ---
    if message.text == "👑 SIGNAL PREMIUM (VIP) 👑":
        if premium_signals_today >= 20:
            bot.send_message(message.chat.id, "🚫 **LIMITE VIP ATTEINTE (20/20)**\n\nReviens demain pour de nouvelles côtes explosives ! 💎")
            return
        
        status_msg = bot.send_message(message.chat.id, "🔥 **CONNEXION AU SERVEUR VIP...**", parse_mode='Markdown')
        time.sleep(2)
        
        premium_signals_today += 1
        côte_vip = round(random.uniform(10.00, 300.00), 2)
        assurance_vip = round(random.uniform(5.00, 15.00), 2)
        
        texte_premium = (
            f"🔱 SIGNAL VIP PREMIUM 🔱\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💰 PRÉVISION : {côte_vip}X+\n"
            f"🛡 SÉCURITÉ : {assurance_vip}X+\n"
            f"📉 RESTANTS : {20 - premium_signals_today}/20\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎁 CODE PROMO : **{CODE_PROMO}**"
        )
        
        markup_vip = telebot.types.InlineKeyboardMarkup()
        markup_vip.add(telebot.types.InlineKeyboardButton("📲 JOUER LE SIGNAL VIP", url=LIEN_INSCRIPTION))
        
        bot.delete_message(message.chat.id, status_msg.message_id)
        try:
            bot.send_video(message.chat.id, ID_VIDEO_UNIQUE, caption=texte_premium, reply_markup=markup_vip, parse_mode='Markdown')
        except:
bot.send_message(message.chat.id, texte_premium, reply_markup=markup_vip, parse_mode='Markdown')
        return

    # --- MODE CLASSIQUE (Côtes 3x à 60x) ---
    if user_id != ADMIN_ID:
        count = user_signals_count.get(user_id, 0)
        if count >= 3:
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("🎁 CRÉER MON COMPTE", url=LIEN_INSCRIPTION))
            bot.send_message(message.chat.id, "🔒 LIMITE 3/3 ATTEINTE**\n\nCrée un compte avec le code **COK225 pour continuer !", reply_markup=markup, parse_mode='Markdown')
            return
        user_signals_count[user_id] = count + 1

    status_msg = bot.send_message(message.chat.id, "🔍 **ANALYSE EN COURS...**", parse_mode='Markdown')
    time.sleep(1.5)
    
    côte = round(random.uniform(3.00, 60.00), 2)
    assurance = round(random.uniform(1.50, 4.00), 2)
    
    now = datetime.now()
    wait_time = random.randint(4, 7)
    time_range = f"{(now + timedelta(minutes=wait_time)).strftime('%H:%M')} - {(now + timedelta(minutes=wait_time+2)).strftime('%H:%M')}"
    
    texte_signal = (
        f"🚀 SIGNAL MEXICAIN225 🧨\n\n"
        f"⏰ HEURE : {time_range}\n"
        f"📈 CÔTE : {côte}X+\n"
        f"🛡 SÉCURITÉ : {assurance}X+\n\n"
        f"🎁 CODE PROMO : **{CODE_PROMO}**"
    )
    
    markup_play = telebot.types.InlineKeyboardMarkup()
    markup_play.add(telebot.types.InlineKeyboardButton("📲 JOUER MAINTENANT", url=LIEN_INSCRIPTION))

    bot.delete_message(message.chat.id, status_msg.message_id)
    
    try:
        bot.send_video(message.chat.id, ID_VIDEO_UNIQUE, caption=texte_signal, reply_markup=markup_play, parse_mode='Markdown')
    except:
        bot.send_message(message.chat.id, texte_signal, reply_markup=markup_play, parse_mode='Markdown')

# --- 4. LANCEMENT SÉCURISÉ ---
if__name__== "__main__":
    # Évite l'erreur 409 Conflict
    bot.remove_webhook()
    time.sleep(1)
    
    # Bot en arrière-plan
    threading.Thread(target=bot.infinity_polling, kwargs={'timeout': 60, 'long_polling_timeout': 60}, daemon=True).start()
    
    # Serveur Flask pour Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
