import telebot, random, os, threading, time
from datetime import datetime, timedelta
from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)

# --- CONFIGURATION ---
API_TOKEN = '8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0' 
ADMIN_ID = 5724620019  
MONGO_URI = "mongodb+srv://mexicain225:03191967@cluster0.zmj8ocq.mongodb.net/" 

bot = telebot.TeleBot(API_TOKEN)

# Connexion MongoDB
client = MongoClient(MONGO_URI)
db = client['luckyjet_db']
users_col = db['users'] 

# --- FONCTIONS BASE DE DONNÉES ---
def get_user(u_id):
    user = users_col.find_one({"_id": u_id})
    if not user:
        user = {"_id": u_id, "count": 0, "is_vip": False}
        users_col.insert_one(user)
    return user

def update_user_count(u_id):
    users_col.update_one({"_id": u_id}, {"$inc": {"count": 1}})

def set_vip(u_id):
    users_col.update_one({"_id": u_id}, {"$set": {"is_vip": True}})

# --- LOGIQUE DU SIGNAL ---
def get_signal():
    now = datetime.now()
    # On génère un signal basé sur l'heure actuelle pour que tout le monde voit le même
    seed_val = now.strftime("%Y%m%d%H%M")
    random.seed(seed_val)
    cote = round(random.uniform(1.5, 15.0), 2)
    prev = round(random.uniform(1.2, 5.0), 2)
    random.seed() # Reset seed
    return cote, prev

# --- COMMANDES BOT ---
@bot.message_handler(commands=['start'])
def start(msg):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 OBTENIR UN SIGNAL")
    bot.send_message(msg.chat.id, "👋 Bienvenue sur le Bot Mexicain225 !", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 OBTENIR UN SIGNAL")
def send_signal(msg):
    u_id = msg.from_user.id
    user_data = get_user(u_id)

    # Vérification Limite (Sauf Admin et VIP)
    if u_id != ADMIN_ID and not user_data['is_vip'] and user_data['count'] >= 3:
        bot.send_message(msg.chat.id, "🚫 **LIMITE ATTEINTE**\n\nTu as déjà utilisé tes 3 signaux gratuits.\n\nInscris-toi sur 1Win avec le code promo **COK225** et envoie ton ID ici pour devenir **VIP ILLIMITÉ** !")
        return

    status = bot.send_message(msg.chat.id, "⏳ Analyse du serveur en cours...")
    time.sleep(1.5)
    bot.delete_message(msg.chat.id, status.message_id)

    cote, prev = get_signal()
    
    if u_id != ADMIN_ID and not user_data['is_vip']:
        update_user_count(u_id)

    txt = f"🚀 **SIGNAL MEXICAIN225** 🧨\n\n⚡️ **CÔTE** : `{cote}X+` \n⚡️ **PRÉVISION** : `{prev}X+` \n⚡️ **ASSURANCE** : `2.00X` \n\n🎁 **CODE PROMO** : `COK225`"
    
    kb = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("📍 JOUER MAINTENANT", url="https://lkbb.cc/e2d8"))
    bot.send_message(msg.chat.id, txt, reply_markup=kb, parse_mode='Markdown')

# --- VALIDATION VIP ---
@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text) >= 7)
def handle_id(msg):
    # Envoie une alerte à l'admin pour valider
    kb = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("✅ VALIDER VIP", callback_data=f"val_{msg.from_user.id}"))
    bot.send_message(ADMIN_ID, f"🔔 **NOUVEL ID REÇU**\nID: `{msg.text}`\nUser: @{msg.from_user.username}", reply_markup=kb)
    bot.send_message(msg.chat.id, "✅ Ton ID a été envoyé pour vérification. Tu recevras une notification dès que ton accès VIP sera activé.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("val_"))
def val_callback(c):
    uid = int(c.data.split("_")[1])
    set_vip(uid)
    bot.send_message(uid, "🌟 **FÉLICITATIONS !**\n\nTon compte a été validé. Tu es désormais membre **VIP ILLIMITÉ** ! Profite bien des signaux 🚀")
    bot.answer_callback_query(c.id, "Utilisateur validé avec succès !")

# --- SERVEUR FLASK POUR RENDER ---
def run_flask():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()
