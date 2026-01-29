import telebot, random, os, threading, time
from datetime import datetime, timedelta
from flask import Flask

app = Flask(__name__)

# --- CONFIGURATION ---
API_TOKEN = '8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0' 
ADMIN_ID = 5724620019  
bot = telebot.TeleBot(API_TOKEN)

CANAL_ID = "@mexicain225officiel"
LIEN_INSCRIPTION = "https://lkbb.cc/e2d8"
CODE_PROMO = "COK225"
ID_VIDEO_UNIQUE = "https://t.me/gagnantpro1xbet/138958" 

DB_FILE = "vip_users.txt"
CONFIG_FILE = "base_minute.txt"

# --- PERSISTENCE ---
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return set(int(l.strip()) for l in f if l.strip().isdigit())
    return set()

def save_user(u_id):
    with open(DB_FILE, "a") as f: f.write(f"{u_id}\n")

def get_base_minute():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            val = f.read().strip()
            return int(val) if val.isdigit() else 23
    return 23

vip_users = load_db()
user_counts = {}

# --- LOGIQUE SYNCHRONISÉE ---
def get_universal_signal():
    now = datetime.now()
    base_minute = get_base_minute()
    current_total = now.hour * 60 + now.minute
    base_total = now.hour * 60 + base_minute
    
    if current_total < base_total:
        base_total -= 60

    next_mins = base_total
    while next_mins <= current_total:
        next_mins += 7
        
    start_time = now.replace(hour=(next_mins // 60) % 24, minute=next_mins % 60, second=0, microsecond=0)
    
    random.seed(start_time.timestamp()) 
    cote = random.randint(30, 150)
    prevision = random.randint(10, 25)
    random.seed() 
    return start_time, cote, prevision

# --- COMMANDES ADMIN ---
@bot.message_handler(commands=['config'])
def config_minute(msg):
    if msg.from_user.id == ADMIN_ID:
        parts = msg.text.split()
        if len(parts) > 1:
            try:
                new_min = int(parts[1])
                if 0 <= new_min < 60:
                    with open(CONFIG_FILE, "w") as f: f.write(str(new_min))
                    bot.send_message(ADMIN_ID, f"✅ Minute de base : `{new_min}`")
                else:
                    bot.send_message(ADMIN_ID, "❌ Entre un nombre entre 0 et 59.")
            except ValueError:
                bot.send_message(ADMIN_ID, "❌ Format : `/config 23`")
        else:
            bot.send_message(ADMIN_ID, "❌ Format : `/config 23`")

# --- ACTIONS ---
@bot.message_handler(commands=['start'])
def start(msg):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 OBTENIR UN SIGNAL")
    bot.send_message(msg.chat.id, f"🔥 **Bienvenue {msg.from_user.first_name} !**", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 OBTENIR UN SIGNAL")
def handle_signal(msg):
    u_id = msg.from_user.id
    count = user_counts.get(u_id, 0)
    
    if u_id != ADMIN_ID and u_id not in vip_users and count >= 3:
        bot.send_message(msg.chat.id, "🚫 **LIMITE ATTEINTE**\n\nInscris-toi avec le code `COK225` pour continuer.")
        return

    status = bot.send_message(msg.chat.id, "⏳ `CALCUL EN COURS...`")
    time.sleep(2)
    bot.delete_message(msg.chat.id, status.message_id)

    start_time, cote, prevision = get_universal_signal()
    time_range = f"{start_time.strftime('%H:%M')} - {(start_time + timedelta(minutes=2)).strftime('%H:%M')}"

    if u_id != ADMIN_ID and u_id not in vip_users:
        user_counts[u_id] = count + 1

    txt = (
        f"🚀 **SIGNAL MEXICAIN225** 🧨\n\n"
        f"⚡️ **TIME** : `{time_range}`\n"
        f"⚡️ **CÔTE** : `{cote}X+` \n"
        f"⚡️ **PRÉVISION** : `{prevision}X+` \n"
        f"⚡️ **ASSURANCE** : `2.50X+` \n\n"
        f"📍 **CLIQUE ICI POUR JOUER**\n"
        f"🎁 **CODE PROMO** : `{CODE_PROMO}`\n\n"
        f"👤 **CONTACT** : @MEXICAINN225"
    )
    kb = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("📍 JOUER", url=LIEN_INSCRIPTION))
    bot.send_video(msg.chat.id, ID_VIDEO_UNIQUE, caption=txt, reply_markup=kb, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text) > 5)
def handle_id(msg):
    kb = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("✅ VALIDER", callback_data=f"val_{msg.from_user.id}"))
    bot.send_message(ADMIN_ID, f"🔔 ID: `{msg.text}`", reply_markup=kb)
    bot.send_message(msg.chat.id, "⏳ ID envoyé pour activation.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("val_"))
def val(c):
    uid = int(c.data.split("_")[1])
    vip_users.add(uid)
    save_user(uid)
    bot.send_message(uid, "🌟 **COMPTE VALIDÉ !**")
    bot.answer_callback_query(c.id, "Validé")

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    def run_bot():
        while True:
            try: bot.infinity_polling(timeout=20)
            except: time.sleep(5)
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
