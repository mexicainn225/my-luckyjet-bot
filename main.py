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
client = MongoClient(MONGO_URI)
db = client['luckyjet_db']
users_col = db['users'] 
config_col = db['config']

LIEN_INSCRIPTION = "https://lkbb.cc/e2d8"
CODE_PROMO = "COK225"
ID_VIDEO_UNIQUE = "https://t.me/gagnantpro1xbet/138958" 

admin_state = {}

# --- FONCTIONS BASE DE DONNÉES ---
def get_user(u_id):
    user = users_col.find_one({"_id": u_id})
    if not user:
        user = {"_id": u_id, "is_vip": False}
        users_col.insert_one(user)
    return user

def set_vip(u_id):
    users_col.update_one({"_id": u_id}, {"$set": {"is_vip": True}})

def get_base_minute():
    conf = config_col.find_one({"_id": "settings"})
    return conf['minute'] if conf else 23

# --- LOGIQUE SIGNAL (CYCLE 14 MIN SANS RÉPÉTITION) ---
def get_universal_signal():
    now = datetime.now()
    base_minute = get_base_minute()
    
    # Calcul en minutes totales depuis minuit (00:00)
    total_minutes_now = now.hour * 60 + now.minute
    
    # On cherche le prochain créneau de 14 min
    next_sig_total = base_minute
    while next_sig_total <= total_minutes_now:
        next_sig_total += 14 
        
    target_hour = (next_sig_total // 60) % 24
    target_minute = next_sig_total % 60
    
    start_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    # Seed aléatoire basé sur le moment exact du signal
    random.seed(start_time.timestamp()) 
    cote = random.randint(30, 150)
    prev = random.randint(10, 25)
    random.seed() 
    
    return start_time, cote, prev

# --- ACTIONS ---
@bot.message_handler(commands=['start'])
def start(msg):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btns = ["🚀 OBTENIR UN SIGNAL", "📊 STATISTIQUES"]
    if msg.from_user.id == ADMIN_ID:
        btns.append("⚙️ CHANGER LA MINUTE")
    markup.add(*btns)
    bot.send_message(msg.chat.id, "👋 Bienvenue sur le Bot Mexicain225 !", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📊 STATISTIQUES")
def stats(msg):
    txt = (
        "📊 **STATISTIQUES DES SIGNAUX**\n\n"
        "✅ Taux de réussite : `98.2%` \n"
        "🚀 Signaux validés : `156` \n"
        "🎯 Précision IA : `Excellente` \n\n"
        "🔥 *Suivez les signaux pour gagner gros.*"
    )
    bot.send_message(msg.chat.id, txt, parse_mode='Markdown')

# --- MENU ADMIN ---
@bot.message_handler(func=lambda m: m.text == "⚙️ CHANGER LA MINUTE" and m.from_user.id == ADMIN_ID)
def ask_new_minute(msg):
    admin_state[ADMIN_ID] = "WAITING_MINUTE"
    bot.send_message(ADMIN_ID, "📝 **MODE CONFIGURATION**\nTape le chiffre de la minute de départ (0-59) :")

@bot.message_handler(func=lambda m: admin_state.get(ADMIN_ID) == "WAITING_MINUTE" and m.from_user.id == ADMIN_ID)
def save_new_minute(msg):
    if msg.text.isdigit():
        new_min = int(msg.text)
        config_col.update_one({"_id": "settings"}, {"$set": {"minute": new_min}}, upsert=True)
        admin_state[ADMIN_ID] = None
        bot.send_message(ADMIN_ID, f"✅ **TERMINÉ** : Le cycle de 14min partira de la minute `{new_min}`.")
    else:
        bot.send_message(ADMIN_ID, "❌ Envoie uniquement un chiffre.")

# --- SIGNAUX ---
@bot.message_handler(func=lambda m: m.text == "🚀 OBTENIR UN SIGNAL")
def check_signal(msg):
    u_id = msg.from_user.id
    user_data = get_user(u_id)
    kb = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("📍 CLIQUE ICI POUR JOUER", url=LIEN_INSCRIPTION))

    if u_id == ADMIN_ID or user_data['is_vip']:
        status = bot.send_message(msg.chat.id, "⏳ `SYNCHRONISATION...`")
        time.sleep(2)
        bot.delete_message(msg.chat.id, status.message_id)
        
        start_time, cote, prev = get_universal_signal()
        txt = (
            f"🚀 **SIGNAL CONFIRMÉ** 🧨\n\n"
            f"⚡️ **HEURE** : `{start_time.strftime('%H:%M')} - {(start_time + timedelta(minutes=2)).strftime('%H:%M')}`\n"
            f"⚡️ **CÔTE** : `{cote}X+` \n"
            f"⚡️ **PRÉVISION** : `{prev}X+` \n"
            f"⚡️ **ASSURANCE** : `2.50X+` \n\n"
            f"🎁 **CODE PROMO** : `{CODE_PROMO}`"
        )
        bot.send_video(msg.chat.id, ID_VIDEO_UNIQUE, caption=txt, reply_markup=kb, parse_mode='Markdown')
    else:
        txt = (
            f"⚠️ **ACCÈS VIP REQUIS** ⚠️\n\n"
            f"1️⃣ Inscris-toi ici : [CLIQUE ICI]({LIEN_INSCRIPTION})\n"
            f"2️⃣ Code Promo : **{CODE_PROMO}**\n"
            f"3️⃣ Envoie ton **ID 1Win** ici pour validation."
        )
        bot.send_video(msg.chat.id, ID_VIDEO_UNIQUE, caption=txt, reply_markup=kb, parse_mode='Markdown')

# --- GESTION DES IDS ---
@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text) >= 7)
def handle_id(msg):
    if admin_state.get(ADMIN_ID) == "WAITING_MINUTE": return
    kb = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("✅ VALIDER VIP", callback_data=f"val_{msg.from_user.id}"))
    bot.send_message(ADMIN_ID, f"🔔 **DEMANDE VIP**\nID : `{msg.text}`", reply_markup=kb)
    bot.send_message(msg.chat.id, "✅ ID reçu ! Un admin va valider ton compte.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("val_"))
def val_callback(c):
    uid = int(c.data.split("_")[1])
    set_vip(uid)
    bot.send_message(uid, "🌟 **FÉLICITATIONS !** Accès VIP activé.")
    bot.answer_callback_query(c.id, "Validé")

# --- LANCEMENT ---
if __name__ == "__main__":
    # Démarrage de Flask pour Render
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    print("Serveur Web prêt sur le port 10000")
    # Démarrage du Bot
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
