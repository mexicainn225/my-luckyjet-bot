import telebot
import random
from datetime import datetime, timedelta

# Ton Token est maintenant bien placé dans une variable
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
    texte = (
        "🤖 **BIENVENUE SUR LUCKY JET PREDICTOR**\n\n"
        "Commandes :\n"
        "🚀 /signal - Signal immédiat\n"
        "📅 /planning - Prochaines failles"
    )
    bot.reply_to(message, texte, parse_mode='Markdown')

@bot.message_handler(commands=['planning'])
def send_planning(message):
    liste = generer_liste_signaux()
    bot.send_message(message.chat.id, f"📅 **PLANNING**\n\n{liste}", parse_mode='Markdown')

@bot.message_handler(commands=['signal'])
def send_instant(message):
    prediction = round(random.uniform(1.20, 3.50), 2)
    bot.send_message(message.chat.id, f"🚀 **CIBLE : {prediction}x**", parse_mode='Markdown')

bot.polling()
