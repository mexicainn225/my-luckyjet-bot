import telebot
import random
from datetime import datetime, timedelta
from flask import Flask
import threading
import os
import time

# --- 1. CONFIGURATION ---
app = Flask(__name__)

# Infos de ton Bot
ADMIN_ID = 5724620019  
API_TOKEN = '8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0'
bot = telebot.TeleBot(API_TOKEN)

# Infos Canal et Liens
CANAL_ID = "@mexicain225officiel" 
LIEN_INSCRIPTION = "https://lkbb.cc/e2d8"
CODE_PROMO = "COK225"
CONTACT_ADMIN = "@MEXICAINN225"

# Lien de ta vidéo Telegram
ID_VIDEO_UNIQUE = "https://t.me/gagnantpro1xbet/138958" 

# Stockage temporaire (Se vide au redémarrage Render)
user_signals_count = {}
registered_users = set()
premium_signals_today = 0
last_reset_date = datetime.now().date()

@app.route('/')
def health_check():
    return "Bot Mexicain is Running!", 200

# --- 2. FONCTIONS DE VÉRIFICATION ---
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

# --- 3. GESTION DES COMMANDES ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    registered_users.add(user_id)
    if not check_sub(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 Rejoindre le Canal", url="https://t.me/mexicain225officiel"))
        bot.send_message(message.chat.id, "👋 **ACCÈS RESTREINT**\n\nRejoins le canal pour activer tes signaux !", reply_markup=markup, parse_mode='Markdown')
        return
    bot.send_message(message.chat.id, "✅ **ACCÈS VALIDÉ**\n\nBienvenue dans l'équipe MEXICAIN225. Choisis une option :", reply_markup=main_menu(), parse_mode='Markdown')

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, f"📊 **STATS ADMIN**\n\n👥 Utilisateurs : {len(registered_users)}\n💎 Premium du jour : {premium_signals_today}/20")

# --- 4. LOGIQUE DES SIGNAUX ---

@bot.message_handler(func=lambda message: message.text in ["🚀 OBTENIR UN SIGNAL", "👑 SIGNAL PREMIUM (VIP) 👑"])
def handle_signals(message):
    global premium_signals_today, last_reset_date
    user_id = message.from_user.id
    
    if not check_sub(user_id):
        bot.reply_to(message, "❌ Tu dois être dans le canal pour utiliser le bot !")
        return

    # Reset de la limite journalière à minuit
    if datetime.now().date() > last_reset_date:
        premium_signals_today = 0
        last_reset_date = datetime.now().date()

    # --- SIGNAL PREMIUM (10x à 300x) ---
    if message.text == "👑 SIGNAL PREMIUM (VIP) 👑":
        if premium_signals_today >= 20:
            bot.send_message(message.chat.id, "🚫 **LIMITE VIP ATTEINTE (20/20)**\n\nLes signaux VIP sont terminés pour aujourd'hui. Reviens demain !")
            return
        
        premium_signals_today += 1
        côte_vip = round(random.uniform(10.00, 300.00), 2)
        assurance = round(random.uniform(5.00, 15.00), 2)
        
        texte_premium = (
            f"🔱 JACKPOT PREMIUM VIP 🔱\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💰 PRÉVISION : {côte_vip}X+\n"
            f"🛡 SÉCURITÉ : {assurance}X+\n"
            f"📉 RESTANTS : {20 - premium_signals_today}/20\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎁 CODE PROMO : **{CODE_PROMO}**\n"
            f"👤 ADMIN : {CONTACT_ADMIN}"
        )
        
        markup_vip = telebot.types.InlineKeyboardMarkup()
        markup_vip.add(telebot.types.InlineKeyboardButton("🔱 JOUER MAINTENANT", url=LIEN_INSCRIPTION))
        
        try:
            bot.send_video(message.chat.
id, ID_VIDEO_UNIQUE, caption=texte_premium, reply_markup=markup_vip, parse_mode='Markdown')
        except:
            bot.send_message(message.chat.id, texte_premium, reply_markup=markup_vip, parse_mode='Markdown')
        return

    # --- SIGNAL CLASSIQUE (3x à 60x) ---
    if user_id != ADMIN_ID:
        count = user_signals_count.get(user_id, 0)
        if count >= 3:
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("🎁 CRÉER MON COMPTE", url=LIEN_INSCRIPTION))
            bot.send_message(message.chat.id, f"🔒 LIMITE 3/3 ATTEINTE**\n\nInscris-toi avec le code **{CODE_PROMO} pour débloquer plus de signaux !", reply_markup=markup, parse_mode='Markdown')
            return
        user_signals_count[user_id] = count + 1

    côte = round(random.uniform(3.00, 60.00), 2)
    assurance = round(random.uniform(1.50, 4.00), 2)
    
    texte_classic = (
        f"🚀 SIGNAL MEXICAIN225 🧨\n\n"
        f"📈 CÔTE VISÉE : {côte}X+\n"
        f"🛡 SÉCURITÉ : {assurance}X+\n\n"
        f"📍 [CLIQUE ICI POUR JOUER]({LIEN_INSCRIPTION})\n"
        f"🎁 CODE PROMO : **{CODE_PROMO}**"
    )
    
    markup_p = telebot.types.InlineKeyboardMarkup()
    markup_p.add(telebot.types.InlineKeyboardButton("📲 JOUER LE SIGNAL", url=LIEN_INSCRIPTION))

    try:
        bot.send_video(message.chat.id, ID_VIDEO_UNIQUE, caption=texte_classic, reply_markup=markup_p, parse_mode='Markdown')
    except:
        bot.send_message(message.chat.id, texte_classic, reply_markup=markup_p, parse_mode='Markdown')

# --- 5. LANCEMENT SÉCURISÉ ---
if __name__== "__main__":
    # Nettoyage des sessions fantômes
    bot.remove_webhook()
    time.sleep(2)
    
    # Bot
    threading.Thread(target=bot.infinity_polling, kwargs={'timeout': 60}, daemon=True).start()
    
    # Serveur
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
