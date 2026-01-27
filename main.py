import telebot
import random
from datetime import datetime, timedelta
from flask import Flask
import threading
import os
import time

# --- 1. CONFIGURATION ---
app = Flask(__name__)

# Ton ID Admin configuré
ADMIN_ID = 5724620019  

# Token et Infos Canal
API_TOKEN = '8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0'
bot = telebot.TeleBot(API_TOKEN)

CANAL_ID = "@mexicain225officiel" 
LIEN_INSCRIPTION = "https://lkbb.cc/e2d8"
CODE_PROMO = "COK225"
CONTACT_ADMIN = "@MEXICAINN225"

# Stockage temporaire des signaux
user_signals_count = {}

# --- 2. SERVEUR DE RÉVEIL (POUR RENDER) ---
@app.route('/')
def health_check():
    return "Bot is alive and running!", 200

# --- 3. FONCTIONS DE VÉRIFICATION ---
def check_sub(user_id):
    if user_id == ADMIN_ID:
        return True
    try:
        member = bot.get_chat_member(CANAL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("🚀 OBTENIR UN SIGNAL"))
    return markup

# --- 4. GESTION DES COMMANDES ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 Rejoindre le Canal", url="https://t.me/mexicain225officiel"))
        bot.send_message(message.chat.id, 
                       "👋 **Bienvenue sur le Bot Lucky Jet MEXICAIN225 !**\n\n"
                       "⚠️ **ACCÈS REFUSÉ**\n\n"
                       "Pour utiliser le bot, tu dois impérativement rejoindre notre canal officiel.", 
                       reply_markup=markup, parse_mode='Markdown')
        return
    
    bot.send_message(message.chat.id, "✅ **Accès validé !**\n\nPrêt à gagner ? Utilise le bouton ci-dessous.", 
                   reply_markup=main_menu(), parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🚀 OBTENIR UN SIGNAL")
def send_signal(message):
    user_id = message.from_user.id
    
    # Vérifications (sauf pour l'admin)
    if user_id != ADMIN_ID:
        if not check_sub(user_id):
            bot.reply_to(message, "❌ Tu dois être dans le canal !")
            return

        count = user_signals_count.get(user_id, 0)
        if count >= 3:
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("🎁 CRÉER MON COMPTE 1WIN", url=LIEN_INSCRIPTION))
            bot.send_message(message.chat.id, 
                             f"🔒 **LIMITE ATTEINTE !**\n\n"
                             f"Pour débloquer les signaux illimités :\n"
                             f"1️⃣ Inscris-toi avec le code : **{CODE_PROMO}**\n"
                             f"2️⃣ Fais un dépôt pour activer ton compte.\n\n"
                             f"Une fois terminé, les signaux seront débloqués à vie ! ✅", 
                             reply_markup=markup, parse_mode='Markdown')
            return
        user_signals_count[user_id] = count + 1

    # --- ANIMATION D'ANALYSE ---
    status_msg = bot.send_message(message.chat.id, "🔍 **Analyse des algorithmes...**", parse_mode='Markdown')
    time.sleep(2)
    bot.edit_message_text("📡 **Connexion au serveur...**", message.chat.id, status_msg.message_id, parse_mode='Markdown')
    time.sleep(2)
    bot.edit_message_text("💎 **GÉNÉRATION DU SIGNAL...**", message.chat.id, status_msg.message_id, parse_mode='Markdown')
    time.sleep(1.5)

    # --- CALCUL DU SIGNAL ---
    now = datetime.now()
    wait_time = random.randint(5, 7)
    time_range = f"{(now + timedelta(minutes=wait_time)).strftime('%H:%M')} - {(now + timedelta(minutes=wait_time+2)).strftime('%H:%M')}"
    
    texte_signal = (
        f"🚀 SIGNAL MEXICAIN225 🧨\n\n"
        f"⚡️ TIME : {time_range}\n"
        f"⚡️ CÔTE : {random.randint(50, 150)}X+\n"
        f"⚡️ PRÉVISION : {random.randint(10, 45)}X+\n"f"⚡️ ASSURANCE : {random.randint(2, 8)}X+\n\n"
        f"📍 [CLIQUE ICI POUR JOUER]({LIEN_INSCRIPTION})\n"
        f"🎁 CODE PROMO : **{CODE_PROMO}**\n\n"
        f"👤 CONTACT : {CONTACT_ADMIN}"
    )
    
    # Envoi du signal et nettoyage
    bot.delete_message(message.chat.id, status_msg.message_id)
    bot.send_message(message.chat.id, texte_signal, parse_mode='Markdown', disable_web_page_preview=True)

    # --- ANNONCE DU PROCHAIN SIGNAL ---
    time.sleep(2)
    bot.send_message(message.chat.id, f"⏳ INFO : Ton prochain signal sera prêt dans environ {wait_time} minutes. Reste attentif ! 🔔")

# --- 5. LANCEMENT DU SERVEUR ---
if name == "__main__":
    # Lancement du bot
    threading.Thread(target=bot.infinity_polling, kwargs={'timeout': 60}, daemon=True).start()
    
    # Lancement de Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
