import telebot, random, os, threading, time
from datetime import datetime, timedelta
from flask import Flask
from pymongo import MongoClient

# --- INITIALISATION FLASK POUR RENDER & CRON-JOB ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Mexicain225 est en ligne ! 🚀"

@app.route('/health')
def health():
    return "OK", 200

# --- CONFIGURATION ---
API_TOKEN = '8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0' 
ADMIN_ID = 5724620019  
MONGO_URI = "mongodb+srv://mexicain225:03191967@cluster0.zmj8ocq.mongodb.net/?retryWrites=true&w=majority" 

bot = telebot.TeleBot(API_TOKEN)

# Connexion MongoDB sécurisée
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client['luckyjet_db']
    users_col = db['users'] 
    config_col = db['config']
    client.server_info() # Test de connexion
except Exception as e:
    print(f"Erreur MongoDB: {e}")

LIEN_INSCRIPTION = "https://lkbb.cc/e2d8"
CODE_PROMO = "COK225"
ID_VIDEO_UNIQUE = "https://t.me/gagnantpro1xbet/138958" 

admin_state = {}

# --- FONCTIONS BASE DE DONNÉES ---
def get_user(u_id):
    try:
        user = users_col.find_one({"_id": u_id})
        if not user:
            user = {"_id": u_id, "is_vip": False}
            users_col.insert_one(user)
        return user
    except:
        return {"_id": u_id, "is_vip": False}

def set_vip(u_id):
    users_col.update_one({"_id": u_id}, {"$set": {"is_vip": True}}, upsert=True)

def get_base_minute():
    try:
        conf = config_col.find_one({"_id": "settings"})
        return conf['minute'] if conf else 23
    except:
        return 23

# --- LOGIQUE SIGNAL (CYCLE 14 MIN FLUIDE) ---
def get_universal_signal():
    now = datetime.now()
    base_minute = get_base_minute()
    total_minutes_now = now.hour * 60 + now.minute
    
    next_sig_total = base_minute
    while next_sig_total <= total_minutes_now:
        next_sig_total += 14 
        
    target_hour = (next_sig_total // 60) % 24
    target_minute = next_sig_total % 60
    
    start_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    random.seed(start_time.timestamp()) 
    cote, prev = random.randint(30, 150), random.randint(10, 25)
    random.seed() 
    return start_time, cote, prev

# --- ACTIONS BOT ---
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
    txt = "📊 **STATISTIQUES**\n\n✅ Succès : `98.2%` \n🎯 Précision IA : `Optimale`"
    bot.send_message(msg.chat.id, txt, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "⚙️ CHANGER LA MINUTE" and m.from_user.id == ADMIN_ID)
def ask_new_minute(msg):
    admin_state[ADMIN_ID] = "WAITING_MINUTE"
    bot.send_message(ADMIN_ID, "📝 Entre la minute de base (0-59) :")

@bot.message_handler(func=lambda m: admin_state.get(ADMIN_ID) == "WAITING_MINUTE" and m.from_user.id == ADMIN_ID)
def save_new_minute(msg):
    if msg.text.isdigit():
        new_min = int(msg.text)
        config_col.update_one({"_id": "settings"}, {"$set": {"minute": new_min}}, upsert=True)
        admin_state[ADMIN_ID] = None
        bot.send_message(ADMIN_ID, f"✅ Minute réglée sur `{new_min}`.")
    else:
        bot.send_message(ADMIN_ID, "❌ Chiffre uniquement.")

@bot.message_handler(func=lambda m: m.text == "🚀 OBTENIR UN SIGNAL")
def check_signal(msg):
    u_id = msg.from_user.id
    user_data = get_user(u_id)
    kb = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("📍 CLIQUE ICI POUR JOUER", url=LIEN_INSCRIPTION))

    if u_id == ADMIN_ID or user_data.get('is_vip'):
        start_time, cote, prev = get_universal_signal()
        txt = (f"🚀 **SIGNAL CONFIRMÉ**\n\n⚡️ **HEURE** : `{start_time.strftime('%H:%M')} - {(start_time + timedelta(minutes=2)).strftime('%H:%M')}`\n"
               f"⚡️ **CÔTE** : `{cote}X+` \n⚡️ **PRÉVISION** : `{prev}X+` \n\n🎁 **CODE** : `{CODE_PROMO}`")
        bot.send_video(msg.chat.id, ID_VIDEO_UNIQUE, caption=txt, reply_markup=kb, parse_mode='Markdown')
    else:
        txt = f"⚠️ **VIP REQUIS**\n\n1️⃣ Inscris-toi : [CLIQUE ICI]({LIEN_INSCRIPTION})\n2️⃣ Code : **{CODE_PROMO}**\n3️⃣ Envoie ton ID ici."
        bot.send_video(msg.chat.id, ID_VIDEO_UNIQUE, caption=txt, reply_markup=kb, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text) >= 7)
def handle_id(msg):
    if admin_state.get(ADMIN_ID) == "WAITING_MINUTE": return
    kb = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("✅ VALIDER VIP", callback_data=f"val_{msg.from_user.id}"))
    bot.send_message(ADMIN_ID, f"🔔 **ID** : `{msg.text}`", reply_markup=kb)
    bot.send_message(msg.chat.id, "✅ ID reçu ! Validation en cours.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("val_"))
def val_callback(c):
    uid = int(c.data.split("_")[1])
    set_vip(uid)
    bot.send_message(uid, "🌟 **VIP ACTIVÉ !**")
    bot.answer_callback_query(c.id, "Validé")

# --- LANCEMENT ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True).start()
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
