import telebot
import random
from datetime import datetime, timedelta
from flask import Flask
import threading
import os

# Configuration du serveur bidon pour Render
app = Flask(__name__)
@app.route('/')
def health_check():
    return "Bot is running", 200

# Ton Token
API_TOKEN = '8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0'
bot = telebot.TeleBot(API_TOKEN)

def generer_liste_signaux():
    signaux = []
    maintenant = datetime.now()
    for i in range(3):
        heure_signal = maintenant + timedelta(minutes=random.randint(5 + (i*15), 15 + (i*20)))
        cote = round(random.uniform(1.50, 5.00), 2)
        signaux.append(f"⏰ {heure_signal.strftime('%H:%M')} ➔ Objectif: {cote}x")
    return "\n".join(signaux)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Création du bouton pour rejoindre le canal
    markup = telebot.types.InlineKeyboardMarkup()
    btn_canal = telebot.types.InlineKeyboardButton("📢 Rejoindre le Canal", url="https://t.me/mexicain225officiel")
    btn_signal = telebot.types.InlineKeyboardButton("🚀 Obtenir un Signal", callback_data="get_signal")
    markup.add(btn_canal)
    markup.add(btn_signal)

    texte = (
        "👋 **Bienvenue sur le Bot Lucky Jet GRATUIT MEXICAIN225 !**\n\n"
        "📢 Pour accéder au bot, rejoignez notre canal :\n"
        "👉 https://t.me/mexicain225officiel\n\n"
        "Clique sur les boutons ci-dessous pour commencer !"
    )
    
    bot.send_message(message.chat.id, texte, reply_markup=markup, parse_mode='Markdown')def send_welcome(message):
    texte = "🤖 **LUCKY JET PREDICTOR ACTIF**\n\n/signal - Pour un signal\n/planning - Pour les failles"
    bot.reply_to(message, texte, parse_mode='Markdown')

@bot.message_handler(commands=['planning'])
def send_planning(message):
    liste = generer_liste_signaux()
    bot.send_message(message.chat.id, f"📅 **PLANNING**\n\n{liste}", parse_mode='Markdown')

@bot.message_handler(commands=['signal'])
def send_instant(message):
    prediction = round(random.uniform(1.20, 3.50), 2)
    bot.send_message(message.chat.id, f"🚀 **CIBLE : {prediction}x**", parse_mode='Markdown')

# Lancement du bot et du serveur en même temps
if __name__== "__main__":
    # Lancer le bot en arrière-plan
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    # Lancer le serveur web demandé par Render
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
