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
ID_VIDEO_PROMO = "https://t.me/gagnantpro1xbet/138958" 

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

# --- LOGIQUE SIGNAL UNIQUE ---
def get_universal_signal():
    now = datetime.now()
    base_minute = get_base_minute()
    current_total = now.hour * 60 + now.minute
    base_total = now.hour * 60 + base_minute
    if current_total < base_total: base_total -= 60
    next_sig = base_total
    while next_sig <= current_total: next_sig += 7
    start_time = now.replace(hour=(next_sig // 60) % 24, minute=next_sig % 60, second=0, microsecond=0)
    
    random.seed(start_time.timestamp()) 
    cote, prev = random.randint(30, 150), random.randint(10, 25)
    random.seed() 
    return start_time, cote, prev

# --- ACTIONS ---
@bot.message_handler(commands=['start'])
def start(msg):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 OBTENIR UN SIGNAL")
    bot.send_message(msg.chat.id, f"👋 Bienvenue sur le Bot Officiel !\n\nUtilise le code promo **{CODE_PROMO}** sur 1Win pour débloquer tes signaux.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 OBTENIR UN SIGNAL")
def check_signal(msg):
    u_id = msg.from_user.id
    user_data = get_user(u_id)

    if u_id == ADMIN_ID or user_data['is_vip']:
        status = bot.send_message(msg.chat.id, "⏳ `ANALYSE DU SERVEUR...`")
        time.sleep(1.5)
        bot.delete_message(msg.chat.id, status.message_id)
        
        # Récupération du temps réel du serveur
        start_time, cote, prev = get_universal_signal()
        
        # APPLICATION DU DÉCALAGE INVISIBLE DE -10 MIN
        display_start = start_time - timedelta(minutes=10)
        display_end = display_start + timedelta(minutes=2)
        
        # Prochain tour calculé avec le même décalage
        next_time_real = start_time + timedelta(minutes=7)
        display_next = next_time_real - timedelta(minutes=10)

        txt = (
            f"🚀 **SIGNAL CONFIRMÉ** 🧨\n\n"
            f"⚡️ **HEURE** : `{display_start.strftime('%H:%M')} - {display_end.strftime('%H:%M')}`\n"
            f"⚡️ **CÔTE** : `{cote}X+` \n"
            f"⚡️ **PRÉVISION** : `{prev}X+` \n\n"
            f"🔜 **PROCHAIN TOUR** : `{display_next.strftime('%H:%M')}`\n\n"
            f"🎁 **CODE** : `{CODE_PROMO}`"
        )
        kb = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("📍 CLIQUE ICI POUR JOUER", url=LIEN_INSCRIPTION))
        bot.send_message(msg.chat.id, txt, reply_markup=kb, parse_mode='Markdown', disable_web_page_preview=True)
    else:
        txt = f"⚠️ **ACCÈS VIP REQUIS**\n\nPour débloquer les signaux illimités :\n1. Inscris-toi ici : [CLIQUE ICI]({LIEN_INSCRIPTION})\n2. Code Promo : **{CODE_PROMO}**\n3. Envoie ton ID 1Win ici."
        kb = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("📍 S'INSCRIRE SUR 1WIN", url=LIEN_INSCRIPTION))
        bot.send_video(msg.chat.id, ID_VIDEO_PROMO, caption=txt, reply_markup=kb, parse_mode='Markdown')

# --- COMMANDES ADMIN ---
@bot.message_handler(commands=['config'])
def config(msg):
    if msg.from_user.id == ADMIN_ID:
        try:
            new_min = int(msg.text.split()[1])
            config_col.update_one({"_id": "settings"}, {"$set": {"minute": new_min}}, upsert=True)
            bot.send_message(ADMIN_ID, f"✅ Configuration mise à jour sur la minute `{new_min}`.")
        except:
            bot.send_message(ADMIN_ID, "❌ Format : `/config 23`")

@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text) >= 7)
def handle_id(msg):
    kb = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("✅ VALIDER VIP", callback_data=f"val_{msg.from_user.id}"))
    bot.send_message(ADMIN_ID, f"🔔 **DEMANDE D'ACCÈS**\nID 1Win : `{msg.text}`\nUser : @{msg.from_user.username}", reply_markup=kb)
    bot.send_message(msg.chat.id, "✅ Ton ID a été envoyé. Un administrateur va valider ton compte sous peu.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("val_"))
def val_callback(c):
    uid = int(c.data.split("_")[1])
    set_vip(uid)
    bot.send_message(uid, "🌟 **FÉLICITATIONS !**\n\nTon accès VIP est maintenant activé. Clique sur le bouton pour ton premier signal !")
    bot.answer_callback_query(c.id, "Utilisateur validé")

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()
    bot.infinity_polling()
