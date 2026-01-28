import telebot
import random
import sqlite3
from datetime import datetime, timedelta
from flask import Flask
import threading
import os
import time

# --- 1. CONFIGURATION ---
app = Flask(__name__)

# Ton token est réintégré ici
API_TOKEN = '8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0'
ADMIN_ID = 5724620019  
bot = telebot.TeleBot(API_TOKEN)

CANAL_ID = "@mexicain225officiel" 
LIEN_INSCRIPTION = "https://lkbb.cc/e2d8"
CODE_PROMO = "COK225"
CONTACT_ADMIN = "@MEXICAINN225"
ID_VIDEO_UNIQUE = "https://t.me/gagnantpro1xbet/138958" 

# --- 2. GESTION DE LA BASE DE DONNÉES ---

def get_db_connection():
    # check_same_thread=False est crucial pour SQLite avec Flask/Threading
    conn = sqlite3.connect('database.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users 
                        (id INTEGER PRIMARY KEY, 
                         count INTEGER DEFAULT 0, 
                         is_registered INTEGER DEFAULT 0, 
                         last_signal_time TEXT)''')
        conn.commit()

init_db()

def get_user_data(user_id):
    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if user:
            return dict(user)
        # Création automatique de l'utilisateur s'il n'existe pas
        conn.execute("INSERT INTO users (id, count, is_registered) VALUES (?, 0, 0)", (user_id,))
        conn.commit()
        return {"id": user_id, "count": 0, "is_registered": 0, "last_signal_time": None}

def update_user(user_id, **kwargs):
    with get_db_connection() as conn:
        for key, value in kwargs.items():
            conn.execute(f"UPDATE users SET {key} = ? WHERE id = ?", (value, user_id))
        conn.commit()

# --- 3. FONCTIONS UTILITAIRES ---

def check_sub(user_id):
    if user_id == ADMIN_ID: return True
    try:
        member = bot.get_chat_member(CANAL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def main_menu(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        telebot.types.KeyboardButton("🚀 OBTENIR UN SIGNAL"),
        telebot.types.KeyboardButton("👑 SIGNAL PREMIUM (VIP) 👑")
    )
    if user_id == ADMIN_ID:
        markup.add(telebot.types.KeyboardButton("📊 STATS ADMIN"))
    return markup

# --- 4. COMMANDES ADMIN ---

@bot.message_handler(commands=['valider'])
def valider_user(message):
    """Commande pour que l'admin active le mode Premium d'un membre"""
    if message.from_user.id == ADMIN_ID:
        try:
            target_id = int(message.text.split()[1])
            update_user(target_id, is_registered=1)
            bot.send_message(message.chat.id, f"✅ L'ID {target_id} est maintenant enregistré comme INSCRIT.", parse_mode='Markdown')
            bot.send_message(target_id, "🎉 Votre accès Premium a été activé ! Vous avez désormais des signaux illimités.")
        except:
            bot.reply_to(message, "❌ Format incorrect. Utilise : `/valider ID_USER`", parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "📊 STATS ADMIN")
def show_stats(message):
    if message.from_user.id == ADMIN_ID:
        with get_db_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            prems = conn.execute("SELECT COUNT(*) FROM users WHERE is_registered = 1").fetchone()[0]
        
        msg = (f"📊 *STATS DU BOT*\n\n"
               f"👥 Utilisateurs totaux : `{total}`\n"
               f"💎 Membres Premium : `{prems}`")
        bot.send_message(message.chat.id, msg, parse_mode='Markdown')

# --- 5. LOGIQUE DES SIGNAUX ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    get_user_data(user_id)
    
    if not check_sub(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.
InlineKeyboardButton("📢 Rejoindre le Canal", url=f"https://t.me/{CANAL_ID[1:]}"))
        bot.send_message(message.chat.id, "👋 *ACCÈS RESTREINT*\nRejoins le canal pour débloquer le bot.", 
                         reply_markup=markup, parse_mode='Markdown')
        return
    
    bot.send_message(message.chat.id, "✅ *ACCÈS VALIDÉ*", reply_markup=main_menu(user_id), parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text in ["🚀 OBTENIR UN SIGNAL", "👑 SIGNAL PREMIUM (VIP) 👑"])
def signal_logic(message):
    user_id = message.from_user.id
    user = get_user_data(user_id)

    if not check_sub(user_id):
        bot.send_message(message.chat.id, "❌ Abonnement expiré ou non trouvé !")
        return

    # --- VERIFICATION INTERVALLE (4-6 MIN) ---
    if user['last_signal_time']:
        last_time = datetime.strptime(user['last_signal_time'], '%Y-%m-%d %H:%M:%S')
        diff = (datetime.now() - last_time).total_seconds() / 60
        if diff < 4:
            wait_time = int(4 - diff)
            bot.send_message(message.chat.id, f"⏳ *PATIENCE*\nProchain signal disponible dans {wait_time} minute(s).")
            return

    # --- LOGIQUE SIGNAL PREMIUM ---
    if message.text == "👑 SIGNAL PREMIUM (VIP) 👑":
        if user['is_registered'] == 0 and user_id != ADMIN_ID:
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("🎁 S'INSCRIRE", url=LIEN_INSCRIPTION))
            bot.send_message(message.chat.id, 
                "🔒 *ACCÈS VIP BLOQUÉ*\n\n"
                "Pour accéder au Premium :\n"
                f"1. Inscris-toi avec le code : `{CODE_PROMO}`\n"
                "2. Fais un dépôt.\n"
                f"3. Envoie ton ID à l'admin : {CONTACT_ADMIN}", 
                reply_markup=markup, parse_mode='Markdown')
            return
        
        cote = round(random.uniform(15.0, 80.0), 2)
        txt = (f"🔱 *SIGNAL VIP PREMIUM*\n"
               f"━━━━━━━━━━━━━━━━━━\n"
               f"💰 CÔTE : {cote}X+\n"
               f"💎 STATUT : CONFIRMÉ\n"
               f"━━━━━━━━━━━━━━━━━━\n"
               f"🎁 CODE : `{CODE_PROMO}`")
        
        btn = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("📲 PLACER LE PARI", url=LIEN_INSCRIPTION))
        bot.send_video(message.chat.id, ID_VIDEO_UNIQUE, caption=txt, reply_markup=btn, parse_mode='Markdown')
        update_user(user_id, last_signal_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # --- LOGIQUE SIGNAL NORMAL ---
    else:
        if user['count'] >= 3 and user['is_registered'] == 0 and user_id != ADMIN_ID:
            bot.send_message(message.chat.id, "🚫 *LIMITE ATTEINTE*\n\nInscris-toi pour avoir des signaux illimités !", parse_mode='Markdown')
            return

        new_count = user['count'] + 1
        cote = round(random.uniform(2.0, 8.0), 2)
        txt = (f"🚀 *SIGNAL NORMAL*\n\n"
               f"📊 CÔTE : {cote}X\n"
               f"🎁 CODE : `{CODE_PROMO}`\n"
               f"👤 CONTACT : {CONTACT_ADMIN}")
        
        btn = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("📲 JOUER MAINTENANT", url=LIEN_INSCRIPTION))
        bot.send_video(message.chat.id, ID_VIDEO_UNIQUE, caption=txt, reply_markup=btn, parse_mode='Markdown')
        
        update_user(user_id, count=new_count, last_signal_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# --- 6. HÉBERGEMENT & LANCEMENT ---

@app.route('/')
def index(): return "Bot Mexicain Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if name == "__main__":
    threading.Thread(target=run_flask).start()
    print("Bot en cours de fonctionnement...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            print(f"Erreur Relance : {e}")
            time.sleep(5)
