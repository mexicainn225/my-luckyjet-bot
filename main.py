import telebot
import random
from datetime import datetime, timedelta
from flask import Flask
import threading
import os

# 1. Configuration
app = Flask(__name__)
@app.route('/')
def health_check():
    return "Bot is running", 200

API_TOKEN = '8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0'
bot = telebot.TeleBot(API_TOKEN)
CANAL_ID = "@mexicain225officiel" # ID du canal pour la vérification
LIEN_INSCRIPTION = "https://lkbb.cc/e2d8"
CODE_PROMO = "COK225"
IMAGE_URL = "https://i.ibb.co/LzNf9fV/luckyjet-banner.jpg" # Tu peux changer ce lien

# Dictionnaire pour compter les signaux par utilisateur
user_signals_count = {}

# Fonction pour vérifier l'abonnement au canal
def check_sub(user_id):
    try:
        member = bot.get_chat_member(CANAL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
        return False

# Menu de boutons (Clavier du bas)
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("🚀 OBTENIR UN SIGNAL"), telebot.types.KeyboardButton("📅 PLANNING"))
    return markup

# 4. Message de Bienvenue avec Image et Vérification
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not check_sub(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 Rejoindre le Canal", url=f"https://t.me/mexicain225officiel"))
        bot.send_photo(message.chat.id, IMAGE_URL, 
                       caption=f"⚠️ **ACCÈS REFUSÉ !**\n\nTu dois rejoindre le canal pour utiliser ce bot gratuitement.\n\nClique ici 👇", 
                       reply_markup=markup, parse_mode='Markdown')
        return

    bot.send_photo(message.chat.id, IMAGE_URL, 
                   caption=f"👋 **Bienvenue sur le Bot Lucky Jet GRATUIT MEXICAIN225 !**\n\nUtilise le menu ci-dessous pour commencer.", 
                   reply_markup=main_menu(), parse_mode='Markdown')

# 5 & 6. Gestion du Signal et Inscription
@bot.message_handler(func=lambda message: message.text == "🚀 OBTENIR UN SIGNAL")
def send_signal(message):
    user_id = message.from_user.id
    
    # Vérification abonnement canal
    if not check_sub(user_id):
        bot.reply_to(message, "❌ Tu as quitté le canal. Rejoins-le pour continuer !")
        return

    # Vérification après 3 signaux (Condition d'inscription)
    count = user_signals_count.get(user_id, 0)
    if count >= 3:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🔗 S'INSCRIRE MAINTENANT", url=LIEN_INSCRIPTION))
        bot.send_message(message.chat.id, 
                         f"🔒 **LIMITE ATTEINTE !**\n\nPour continuer à recevoir des signaux illimités, tu dois :\n1. T'inscrire sur 1win avec le code : **{CODE_PROMO}**\n2. Déposer sur ton compte.\n\nUne fois fait, clique sur le bouton ci-dessous !", 
                         reply_markup=markup, parse_mode='Markdown')
        # On ne reset pas le compteur ici pour forcer l'action
        return

    # Génération du signal au format demandé
    now = datetime.now()
    time_range = f"{(now + timedelta(minutes=2)).strftime('%H:%M')} - {(now + timedelta(minutes=4)).strftime('%H:%M')}"
    cote = f"{random.randint(50, 150)}X+"
    prevision = f"{random.randint(10, 45)}X+"
    assurance = f"{random.randint(2, 8)}X+"
    
    texte_signal = (
        f"🚀 SIGNAL MEXICAIN225 🧨\n\n"
        f"⚡️ TIME : {time_range}\n"
        f"⚡️ CÔTE : {cote}\n"
        f"⚡️ PRÉVISION : {prevision}\n"
        f"⚡️ ASSURANCE : {assurance}\n\n"
        f"📍 [CLIQUE ICI POUR JOUER]({LIEN_INSCRIPTION})\n"
        f"🎁 CODE PROMO : **{CODE_PROMO}**"
    )
    
    bot.send_message(message.chat.id, texte_signal, parse_mode='Markdown', disable_web_page_preview=True)
    
    # Augmenter le compteur de l'utilisateur
    user_signals_count[user_id] = count + 1

# 7. Commande Planning
@bot.message_handler(func=lambda message: message.text == "📅 PLANNING")
def send_planning(message):
    signaux = []
    maintenant = datetime.now()
    for i in range(3):
        heure = (maintenant + timedelta(minutes=random.randint(10, 60))).strftime('%H:%M')
        signaux.append(f"⏰ {heure} ➔ Objectif: {random.randint(2, 10)}x")
    
    bot.send_message(message.chat.id, "📅 **PLANNING DES PROCHAINES FAILLES**\n\n" + "\n".join(signaux), parse_mode='Markdown')

# Lancement
if name == "__main__":
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
