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

# --- LOGIQUE SIGNAL UNIQUE (CYCLE 14 MIN) ---
def get_universal_signal():
    now = datetime.now()
    base_minute = get_base_minute()
    
    current_total = now.hour * 60 + now.minute
    base_total = now.hour * 60 + base_minute
    
    if current_total < base_total:
        base_total -= 60

    # STRATÉGIE : On saute de 14 minutes au lieu de 7
    next_sig = base_total
    while next_sig <= current_total:
        next_sig += 14 # Cycle de 14 minutes
        
    start_time = now.replace(hour=(next_sig // 60) % 24, minute=next_sig % 60, second=0, microsecond=0)
    
    random.seed(start_time.timestamp()) 
    cote = random.randint(30, 150)
    prev = random.randint(10, 25)
    random.seed() 
    
    return start_time, cote, prev

# --- ACTIONS ---
@bot.message_handler(commands=['start'])
def start(msg):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 OBTENIR UN SIGNAL")
    bot.send_message(msg.chat.id, "👋 Bienvenue ! Inscris-toi pour débloquer les signaux VIP (Cycle 14 min).", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 OBTENIR UN SIGNAL")
def check_signal(msg):
    u_id = msg.from_user.id
    user_data = get_user(u_id)

    if u_id == ADMIN_ID or user_data['is_vip']:
        status = bot.send_message(msg.chat.id, "⏳ `ANALYSE DES DONNÉES (14 MIN)...`")
        time.sleep(1.5)
        bot.delete_message(msg.chat.id, status.message_id)
        
        start_time, cote, prev = get_universal_signal()
        end_time = start_time + timedelta(minutes=2)
        
        txt = (
            f"🚀 **SIGNAL VIP (CYCLE 14 MIN)** 🧨\n\n"
            f"⚡️ **HEURE** : `{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}`\n"
            f"⚡️ **CÔTE** : `{cote}X+` \n"
            f"⚡️ **PRÉVISION** : `{prev}X+` \n\n"
            f"📍 **[CLIQUE ICI POUR JOUER]({LIEN_INSCRIPTION})**"
        )
        bot.send_message(msg.chat.id, txt, parse_mode='Markdown', disable_web_page_preview=True)
    else:
        txt = f"⚠️ **ACCÈS VIP REQUIS**\n\n1. Inscris-toi : [CLIQUE ICI]({LIEN_INSCRIPTION})\n2. Code Promo : **{CODE_PROMO}**\n3. Envoie ton ID ici pour validation."
        kb = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("📍 S'INSCRIRE", url=LIEN_INSCRIPTION))
        bot.send_video(msg.chat.id, ID_VIDEO_PROMO, caption=txt, reply_markup=kb, parse_mode='Markdown')

# --- COMMANDES ADMIN ---
@bot.message_handler(commands=['config'])
def set_config(msg):
    if msg.from_user.id == ADMIN_ID:
        try:
            new_min = int(msg.text.split()[1])
            config_col.update_one({"_id": "settings"}, {"$set": {"minute": new_min}}, upsert=True)
            bot.send_message(ADMIN_ID, f"✅ Base réglée sur la minute `{new_min}`. Intervalle : 14 minutes.")
        except:
            bot.send_message(ADMIN_ID, "❌ Utilise : `/config 23`")

@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text) >= 7)
def handle_id(msg):
    kb = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("✅ VALIDER VIP", callback_data=f"val_{msg.from_user.id}"))
    bot.send_message(ADMIN_ID, f"🔔 **NOUVEL ID** : `{msg.text}`", reply_markup=kb)
    bot.send_message(msg.chat.id, "✅ ID reçu ! Un administrateur va valider ton compte d'ici peu.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("val_"))
def val_callback(c):
    uid = int(c.data.split("_")[1])
    set_vip(uid)
    bot.send_message(uid, "🌟 **FÉLICITATIONS !** Ton accès VIP est activé. Tu peux maintenant obtenir les signaux !")
    bot.answer_callback_query(c.id, "Validé !")

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()
    bot.infinity_polling()
