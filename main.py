import telebot
import random
from datetime import datetime, timedelta
from flask import Flask
import threading
import os

# 1. Configuration du serveur Web (pour Render)
app = Flask(__name__)
@app.route('/')
def health_check():
    return "Bot is running", 200

# 2. Paramètres du Bot
API_TOKEN = '8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0'
bot = telebot.TeleBot(API_TOKEN)
CANAL_ID = "@mexicain225officiel" 
LIEN_INSCRIPTION = "https://lkbb.cc/e2d8"
CODE_PROMO = "COK225"

# Dictionnaire pour compter les signaux
user_signals_count = {}

# 3. Fonction de vérification d'abonnement
def check_sub(user_id):
    try:
        member = bot.get_chat_member(CANAL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"Erreur vérification abonnement: {e}")
        return False

# 4. Menu principal avec boutons
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("🚀 OBTENIR UN SIGNAL"))
    markup.add(telebot.types.KeyboardButton("📅 PLANNING"))
    return markup

# 5. Gestion de la commande /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 Rejoindre le Canal", url="https://t.me/mexicain225officiel"))
        bot.send_message(message.chat.id, 
                       "👋 **Bienvenue sur le Bot Lucky Jet GRATUIT MEXICAIN225 !**\n\n"
                       "⚠️ **ACCÈS REFUSÉ**\n\n"
                       "Pour utiliser le bot, tu dois impérativement rejoindre notre canal officiel ci-dessous.", 
                       reply_markup=markup, parse_mode='Markdown')
        return

    bot.send_message(message.chat.id, 
                   "✅ **Accès validé !**\n\nUtilise le menu ci-dessous pour générer tes signaux Lucky Jet.", 
                   reply_markup=main_menu(), parse_mode='Markdown')

# 6. Gestion du bouton SIGNAL
@bot.message_handler(func=lambda message: message.text == "🚀 OBTENIR UN SIGNAL")
def send_signal(message):
    user_id = message.from_user.id
    
    if not check_sub(user_id):
        bot.reply_to(message, "❌ Tu dois être dans le canal pour voir les signaux !")
        return

    # Vérification après 3 signaux
    count = user_signals_count.get(user_id, 0)
    if count >= 3:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🔗 S'INSCRIRE SUR 1WIN", url=LIEN_INSCRIPTION))
        bot.send_message(message.chat.id, 
                         f"🔒 **LIMITE ATTEINTE !**\n\n"
                         f"Pour continuer à recevoir des signaux, tu dois :\n"
                         f"1️⃣ T'inscrire via le bouton ci-dessous\n"
                         f"2️⃣ Utiliser le code promo : **{CODE_PROMO}**\n"
                         f"3️⃣ Faire un dépôt minimum.\n\n"
                         f"Une fois ton compte créé, les signaux seront débloqués !", 
                         reply_markup=markup, parse_mode='Markdown')
        return

    # Génération du signal
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
    user_signals_count[user_id] = count + 1

# 7. Gestion du bouton PLANNING
@bot.message_handler(func=lambda message: message.
text == "📅 PLANNING")
def send_planning(message):
    maintenant = datetime.now()
    liste = []
    for i in range(3):
        h = (maintenant + timedelta(minutes=random.randint(15, 120))).strftime('%H:%M')
        liste.append(f"⏰ {h} ➔ Objectif: {random.randint(2, 15)}x")
    
    bot.send_message(message.chat.id, "📅 **PLANNING DES PROCHAINES FAILLES**\n\n" + "\n".join(liste), parse_mode='Markdown')

# 8. Lancement final
if __name__== "__main__":
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
