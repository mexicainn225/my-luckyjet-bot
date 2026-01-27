import telebot
import random
from datetime import datetime, timedelta
from flask import Flask
import threading
import os

# --- CONFIGURATION ---
app = Flask(__name__)

# Ton ID Admin est maintenant configuré
ADMIN_ID = 5724620019  

API_TOKEN = '8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0'
bot = telebot.TeleBot(API_TOKEN)

CANAL_ID = "@mexicain225officiel" 
LIEN_INSCRIPTION = "https://lkbb.cc/e2d8"
CODE_PROMO = "COK225"
CONTACT_ADMIN = "@MEXICAINN225"

user_signals_count = {}

# --- SERVEUR DE RÉVEIL POUR RENDER ---
@app.route('/')
def health_check():
    return "Bot is alive and running!", 200

# --- LOGIQUE DU BOT ---

def check_sub(user_id):
    # Si c'est toi, accès illimité garanti
    if user_id == ADMIN_ID:
        return True
    try:
        member = bot.get_chat_member(CANAL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("🚀 OBTENIR UN SIGNAL"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 Rejoindre le Canal", url="https://t.me/mexicain225officiel"))
        bot.send_message(message.chat.id, "⚠️ **ACCÈS REFUSÉ**\n\nRejoins le canal pour continuer.", reply_markup=markup, parse_mode='Markdown')
        return
    bot.send_message(message.chat.id, "✅ **Accès validé !**", reply_markup=main_menu(), parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🚀 OBTENIR UN SIGNAL")
def send_signal(message):
    user_id = message.from_user.id
    
    # Vérifications uniquement pour les utilisateurs normaux
    if user_id != ADMIN_ID:
        if not check_sub(user_id):
            bot.reply_to(message, "❌ Abonne-toi au canal !")
            return
            
        count = user_signals_count.get(user_id, 0)
        if count >= 3:
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("🔗 S'INSCRIRE SUR 1WIN", url=LIEN_INSCRIPTION))
            bot.send_message(message.chat.id, f"🔒 LIMITE ATTEINTE !**\n\nInscris-toi avec le code **{CODE_PROMO} pour débloquer.", reply_markup=markup, parse_mode='Markdown')
            return
        user_signals_count[user_id] = count + 1

    # Génération du signal (Intervalle de 5 à 7 minutes)
    now = datetime.now()
    start_min = random.randint(5, 7)
    end_min = start_min + 2
    
    time_range = f"{(now + timedelta(minutes=start_min)).strftime('%H:%M')} - {(now + timedelta(minutes=end_min)).strftime('%H:%M')}"
    
    texte_signal = (
        f"🚀 SIGNAL MEXICAIN225 🧨\n\n"
        f"⚡️ TIME : {time_range}\n"
        f"⚡️ CÔTE : {random.randint(50, 150)}X+\n"
        f"⚡️ PRÉVISION : {random.randint(10, 45)}X+\n"
        f"⚡️ ASSURANCE : {random.randint(2, 8)}X+\n\n"
        f"📍 [CLIQUE ICI POUR JOUER]({LIEN_INSCRIPTION})\n"
        f"🎁 CODE PROMO : **{CODE_PROMO}**\n\n"
        f"👤 CONTACT : {CONTACT_ADMIN}"
    )
    
    bot.send_message(message.chat.id, texte_signal, parse_mode='Markdown', disable_web_page_preview=True)

# --- LANCEMENT ---
if __name__== "__main__":
    # On retire 'non_stop' des kwargs car infinity_polling le gère déjà
    threading.Thread(target=bot.infinity_polling, kwargs={'timeout': 60}, daemon=True).start()
    
    # Port Render (par défaut 10000)
    port = int(os.environ.get("PORT", 10000))
    
    # Lancement de Flask
    app.run(host='0.0.0.0', port=port)
