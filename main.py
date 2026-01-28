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

DB_FILE = "validated_users.txt"
USAGE_FILE = "usage_stats.txt"

# --- PERSISTENCE ---
def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return set(int(l.strip()) for l in f if l.strip().isdigit())
    return set()

def load_usage():
    usage = {}
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            for line in f:
                if ":" in line:
                    u_id, count = line.strip().split(":")
                    usage[int(u_id)] = int(count)
    return usage

def save_usage(u_id, count):
    usage_data = load_usage()
    usage_data[u_id] = count
    with open(USAGE_FILE, "w") as f:
        for uid, c in usage_data.items(): f.write(f"{uid}:{c}\n")

validated_users = load_users()
user_signals_count = load_usage()
last_signal_end_time = {}

# --- LOGIQUE ---
def check_sub(u_id):
    if u_id == ADMIN_ID: return True
    try:
        m = bot.get_chat_member(CANAL_ID, u_id)
        return m.status in ['member', 'administrator', 'creator']
    except: return False

def main_menu(u_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(telebot.types.KeyboardButton("🚀 OBTENIR UN SIGNAL"))
    if u_id in validated_users or u_id == ADMIN_ID:
        markup.add(telebot.types.KeyboardButton("👑 SIGNAL PREMIUM 👑"))
    if u_id == ADMIN_ID:
        markup.add(telebot.types.KeyboardButton("📊 STATS ADMIN"))
    return markup

@bot.message_handler(commands=['start'])
def start(msg):
    u_id = msg.from_user.id
    if not check_sub(u_id):
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("📢 Rejoindre le Canal", url=f"https://t.me/{CANAL_ID[1:]}"))
        bot.send_message(msg.chat.id, "❌ **ACCÈS REFUSÉ**\n\nRejoins d'abord le canal !", reply_markup=kb, parse_mode='Markdown')
        return
    bot.send_message(msg.chat.id, f"🔥 **Bienvenue {msg.from_user.first_name} !**", reply_markup=main_menu(u_id), parse_mode='Markdown')

# --- SYSTÈME DE SIGNAUX ---
@bot.message_handler(func=lambda m: m.text in ["🚀 OBTENIR UN SIGNAL", "👑 SIGNAL PREMIUM 👑"])
def signal_logic(msg):
    u_id = msg.from_user.id
    is_premium_btn = "PREMIUM" in msg.text
    now = datetime.now()

    # Bloquer si un signal est encore valide
    if u_id in last_signal_end_time and now < last_signal_end_time[u_id]:
        diff = last_signal_end_time[u_id] - now
        bot.reply_to(msg, f"⏳ Un signal est déjà en cours. Attends la fin de sa validité.")
        return

    # Vérification Premium
    if is_premium_btn and u_id not in validated_users and u_id != ADMIN_ID:
        bot.reply_to(msg, "⛔ **ACCÈS PREMIUM REQUIS**\n\nEnvoie ton ID pour validation.")
        return

    # Limite gratuit
    count = user_signals_count.get(u_id, 0)
    if not is_premium_btn and u_id not in validated_users and u_id != ADMIN_ID and count >= 3:
        bot.send_message(msg.chat.id, "🚫 Limite gratuite atteinte. Passe au Premium !")
        return

    # Calcul des temps
    start_time = now + timedelta(minutes=1)
    # 2 minutes pour le format premium demandé, 5-6 pour le format précédent
    duration = 2 if is_premium_btn else random.randint(5, 6)
    end_time = start_time + timedelta(minutes=duration)
    last_signal_end_time[u_id] = end_time
    time_range = f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"

    # Design et Cotes
    if is_premium_btn:
        cote = f"{random.randint(10, 300)}X+"
        prevision = f"{random.randint(5, 50)}X+"
        assurance = f"{random.randint(2, 10)}X+"
        
        txt = (
            f"🚀 **SIGNAL MEXICAIN225** 🧨\n\n"
            f"⚡️ **TIME** : `{time_range}`\n"
            f"⚡️ **CÔTE** : `{cote}`\n"
            f"⚡️ **PRÉVISION** : `{prevision}`\n"
            f"⚡️ **ASSURANCE** : `{assurance}`\n\n"
            f"📍 **CLIQUE ICI POUR JOUER**\n"
            f"🎁 **CODE PROMO** : `{CODE_PROMO}`\n\n"
            f"👤 **CONTACT** : @MEXICAINN225"
        )
    else:
        user_signals_count[u_id] = count + 1
        save_usage(u_id, count + 1)
        cote = f"{random.randint(3, 30)}X+"
        assurance = f"{random.randint(1, 5)}X+"
        
        txt = (
            f"🚀 **GRAND SIGNAL** 🧨\n\n"
            f"🧨 **TIME** : `{time_range}`\n"
            f"🧨 **SIGNAL** : `{cote}`\n"
            f"🧨 **ASSURANCE** : `{assurance}`\n\n"
            f"✅ **CLIQUE ICI POUR JOUER**\n"
            f"🎁 **CODE PROMO** : `{CODE_PROMO}`\n\n"
            f"👤 **CONTACT** : @MEXICAINN225"
        )

    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("📍 CLIQUE ICI POUR JOUER", url=LIEN_INSCRIPTION))
    bot.send_video(msg.chat.id, ID_VIDEO_UNIQUE, caption=txt, reply_markup=kb, parse_mode='Markdown')

# --- VALIDATION ID ---
@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text) > 5)
def register_id(msg):
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("✅ CONFIRMER PREMIUM", callback_data=f"vip_{msg.from_user.id}"))
    bot.send_message(ADMIN_ID, f"🔔 **DEMANDE VIP**\nUser: {msg.from_user.first_name}\nID: `{msg.text}`", reply_markup=kb, parse_mode='Markdown')
    bot.send_message(msg.chat.id, "⏳ ID envoyé à l'admin pour vérification.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("vip_"))
def confirm_vip(c):
    target_id = int(c.data.split("_")[1])
    if target_id not in validated_users:
        validated_users.add(target_id)
        with open(DB_FILE, "a") as f: f.write(f"{target_id}\n")
        bot.send_message(target_id, "🌟 **PREMIUM ACTIVÉ !**", reply_markup=main_menu(target_id))
    bot.edit_message_text(f"✅ User {target_id} validé !", ADMIN_ID, c.message.message_id)

if __name__ == "__main__":
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
