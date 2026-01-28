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
    conn = sqlite3.connect('database.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS users 
                        (id INTEGER PRIMARY KEY, 
                         count INTEGER DEFAULT 0, 
                         is_registered INTEGER DEFAULT 0, 
                         last_signal_time TEXT)''')
        conn.commit()
    except Exception as e:
        print(f"Erreur DB init: {e}")
    finally:
        conn.close()

init_db()

def get_user_data(user_id):
    conn = get_db_connection()
    try:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if user:
            return dict(user)
        conn.execute("INSERT INTO users (id, count, is_registered) VALUES (?, 0, 0)", (user_id,))
        conn.commit()
        return {"id": user_id, "count": 0, "is_registered": 0, "last_signal_time": None}
    finally:
        conn.close()

def update_user_db(user_id, **kwargs):
    conn = get_db_connection()
    try:
        for key, value in kwargs.items():
            conn.execute(f"UPDATE users SET {key} = ? WHERE id = ?", (value, user_id))
        conn.commit()
    finally:
        conn.close()

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
    if message.from_user.id == ADMIN_ID:
        try:
            target_id = int(message.text.split()[1])
            update_user_db(target_id, is_registered=1)
            bot.send_message(message.chat.id, f"✅ ID {target_id} validé !", parse_mode='Markdown')
            bot.send_message(target_id, "🎉 Votre accès Premium est activé !")
        except:
            bot.reply_to(message, "❌ Utilise : /valider ID_USER")

@bot.message_handler(func=lambda message: message.text == "📊 STATS ADMIN")
def show_stats(message):
    if message.from_user.id == ADMIN_ID:
        conn = get_db_connection()
        total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        prems = conn.execute("SELECT COUNT(*) FROM users WHERE is_registered = 1").fetchone()[0]
        conn.close()
        bot.send_message(message.chat.id, f"📊 Utilisateurs : {total}\n💎 Premium : {prems}")

# --- 5. LOGIQUE DES SIGNAUX ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    get_user_data(user_id)
    if not check_sub(user_id):
        btn = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("📢 Canal", url=f"https://t.me/{CANAL_ID[1:]}"))
        bot.send_message(message.chat.id, "👋 Rejoins le canal !", reply_markup=btn)
        return
    bot.send_message(message.chat.id, "✅ Accès validé", reply_markup=main_menu(user_id))

@bot.message_handler(func=lambda message: message.
text in ["🚀 OBTENIR UN SIGNAL", "👑 SIGNAL PREMIUM (VIP) 👑"])
def signal_logic(message):
    user_id = message.from_user.id
    user = get_user_data(user_id)

    if not check_sub(user_id):
        bot.send_message(message.chat.id, "❌ Abonne-toi au canal !")
        return

    # Intervalle 4 min
    if user['last_signal_time']:
        last_time = datetime.strptime(user['last_signal_time'], '%Y-%m-%d %H:%M:%S')
        diff = (datetime.now() - last_time).total_seconds() / 60
        if diff < 4:
            bot.send_message(message.chat.id, f"⏳ Attends {int(4 - diff)} min.")
            return

    if message.text == "👑 SIGNAL PREMIUM (VIP) 👑":
        if user['is_registered'] == 0 and user_id != ADMIN_ID:
            btn = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("🎁 S'inscrire", url=LIEN_INSCRIPTION))
            bot.send_message(message.chat.id, "🔒 Section réservée aux inscrits.", reply_markup=btn)
            return
        
        cote = round(random.uniform(15.0, 90.0), 2)
        txt = f"🔱 *VIP PREMIUM*\n💰 CÔTE : {cote}X\n🎁 CODE : `{CODE_PROMO}`"
        bot.send_video(message.chat.id, ID_VIDEO_UNIQUE, caption=txt, parse_mode='Markdown')
        update_user_db(user_id, last_signal_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    else:
        if user['count'] >= 3 and user['is_registered'] == 0 and user_id != ADMIN_ID:
            bot.send_message(message.chat.id, "🚫 Limite atteinte. Inscris-toi !")
            return

        cote = round(random.uniform(1.8, 6.5), 2)
        txt = f"🚀 *NORMAL*\n📊 CÔTE : {cote}X\n🎁 CODE : `{CODE_PROMO}`"
        bot.send_video(message.chat.id, ID_VIDEO_UNIQUE, caption=txt, parse_mode='Markdown')
        update_user_db(user_id, count=user['count'] + 1, last_signal_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# --- 6. LANCEMENT ---

@app.route('/')
def index(): return "Bot Online", 200

if __name__== "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except:
            time.sleep(5)
