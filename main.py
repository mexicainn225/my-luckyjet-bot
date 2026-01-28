import telebot
import random
from datetime import datetime, timedelta
from flask import Flask
import threading
import os
import time

# --- 1. CONFIGURATION ---
app = Flask(__name__)

# Ton Token directement intégré
API_TOKEN = '8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0'
ADMIN_ID = 5724620019  
bot = telebot.TeleBot(API_TOKEN)

CANAL_ID = "@mexicain225officiel" 
LIEN_INSCRIPTION = "https://lkbb.cc/e2d8"
CODE_PROMO = "COK225"
CONTACT_ADMIN = "@MEXICAINN225"
ID_VIDEO_UNIQUE = "https://t.me/gagnantpro1xbet/138958" 

# --- GESTION DE LA PERSISTANCE ---
DB_FILE = "validated_users.txt"

def load_validated_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return set(int(line.strip()) for line in f if line.strip().isdigit())
    return set()

def save_user(user_id):
    validated_users.add(user_id)
    with open(DB_FILE, "a") as f:
        f.write(f"{user_id}\n")

# Initialisation
validated_users = load_validated_users()
user_signals_count = {}
last_signal_expiry = {} 

@app.route('/')
def health_check():
    return "Bot Mexicain Operational", 200

# --- 2. FONCTIONS DE VÉRIFICATION ---

def check_sub(user_id):
    if user_id == ADMIN_ID: return True
    try:
        member = bot.get_chat_member(CANAL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def main_menu(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(telebot.types.KeyboardButton("🚀 OBTENIR UN SIGNAL"))
    if user_id in validated_users or user_id == ADMIN_ID:
        markup.add(telebot.types.KeyboardButton("👑 SIGNAL PREMIUM 👑"))
    return markup

# --- 3. COMMANDES ET VALIDATION ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 Rejoindre le Canal", url=f"https://t.me/{CANAL_ID.replace('@','')}"))
        bot.send_message(message.chat.id, "👋 **ACCÈS PRIVÉ**\nRejoins le canal pour activer le bot.", reply_markup=markup, parse_mode='Markdown')
        return
    bot.send_message(message.chat.id, "✅ **ACCÈS VALIDÉ**", reply_markup=main_menu(user_id))

@bot.message_handler(func=lambda message: message.text.isdigit() and len(message.text) > 5)
def handle_id_submission(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    id_1xbet = message.text

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("✅ Valider l'accès", callback_data=f"accept_{user_id}"))
    
    bot.send_message(ADMIN_ID, f"🔔 **DEMANDE DE VALIDATION**\n\nUtilisateur : {user_name}\nID 1xBet : `{id_1xbet}`", 
                     parse_mode='Markdown', reply_markup=markup)
    
    bot.send_message(message.chat.id, "⏳ **DEMANDE ENVOYÉE !**\nL'admin vérifie ton inscription. Tu recevras une notification sous peu.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_"))
def admin_validation(call):
    target_user_id = int(call.data.split("_")[1])
    if target_user_id not in validated_users:
        save_user(target_user_id)
    
    try:
        bot.send_message(target_user_id, "🎉 **FÉLICITATIONS !**\nTon compte a été validé.", 
                         reply_markup=main_menu(target_user_id))
        bot.edit_message_text(f"✅ Utilisateur {target_user_id} validé !", chat_id=ADMIN_ID, message_id=call.message.message_id)
    except:
        bot.answer_callback_query(call.id, "Erreur lors de la notification.")

# --- 4. LOGIQUE DES SIGNAUX AVEC ATTENTE ---

@bot.message_handler(func=lambda message: message.text in ["🚀 OBTENIR UN SIGNAL", "👑 SIGNAL PREMIUM 👑"])
def handle_signals(message):
    user_id = message.from_user.id
    now = datetime.now()

    # Vérification anti-spam (attente de la fin du signal précédent)
    if user_id in last_signal_expiry:
        if now < last_signal_expiry[user_id]:diff = last_signal_expiry[user_id] - now
            mins, secs = divmod(int(diff.total_seconds()), 60)
            bot.reply_to(message, f"⏳ VEUILLEZ PATIENTER**\n\nL'analyse précédente est encore en cours de validité.\nNouvelle analyse disponible dans : **{mins}m {secs}s.")
            return

    if not check_sub(user_id):
        bot.reply_to(message, "❌ Abonne-toi au canal !")
        return

    # Limite gratuite
    count = user_signals_count.get(user_id, 0)
    if user_id != ADMIN_ID and user_id not in validated_users and count >= 3:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🎁 M'INSCRIRE", url=LIEN_INSCRIPTION))
        bot.send_message(message.chat.id, "🔒 **LIMITE GRATUITE ATTEINTE !**\nInscris-toi pour continuer.", reply_markup=markup)
        return

    # Création du signal
    wait = random.randint(3, 6)
    duree = 2
    time_start_dt = now + timedelta(minutes=wait)
    time_end_dt = time_start_dt + timedelta(minutes=duree)
    
    last_signal_expiry[user_id] = time_end_dt # Bloquer jusqu'à la fin

    time_range = f"{time_start_dt.strftime('%H:%M')} - {time_end_dt.strftime('%H:%M')}"

    if "PREMIUM" in message.text:
        cote, prev, assu = random.randint(50, 200), random.randint(20, 45), random.randint(8, 15)
        titre = "🚀 SIGNAL PREMIUM 👑"
    else:
        user_signals_count[user_id] = count + 1
        cote, prev, assu = random.randint(3, 60), random.randint(10, 25), random.randint(2, 7)
        titre = "🚀 SIGNAL MEXICAIN225 🧨"

    texte = (
        f"{titre}\n\n"
        f"⌚️ TIME : {time_range}\n"
        f"📈 CÔTE : {cote}X+\n"
        f"🎯 PRÉVISION : {prev}X+\n"
        f"🛡 ASSURANCE : {assu}X+\n\n"
        f"📍 [CLIQUE ICI POUR JOUER]({LIEN_INSCRIPTION})\n"
        f"🎁 CODE PROMO : **{CODE_PROMO}**"
    )

    markup_play = telebot.types.InlineKeyboardMarkup()
    markup_play.add(telebot.types.InlineKeyboardButton("📲 JOUER MAINTENANT", url=LIEN_INSCRIPTION))
    
    bot.send_video(message.chat.id, ID_VIDEO_UNIQUE, caption=texte, reply_markup=markup_play, parse_mode='Markdown')

# --- 5. RUN ---
if name == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    threading.Thread(target=bot.infinity_polling, kwargs={'timeout': 60}, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
