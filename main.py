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
USAGE_FILE = "usage_stats.txt"

# --- PERSISTENCE ---
def load_db(file):
    if os.path.exists(file):
        with open(file, "r") as f: return set(int(l.strip()) for l in f if l.strip().isdigit())
    return set()

def save_user(file, u_id):
    with open(file, "a") as f: f.write(f"{u_id}\n")

def load_usage():
    usage = {}
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            for line in f:
                if ":" in line:
                    u_id, count = line.strip().split(":")
                    usage[int(u_id)] = int(count)
    return usage

vip_users = load_db(DB_FILE)
user_counts = load_usage()
last_signal_time = {}

# --- LOGIQUE ---
def check_sub(u_id):
    if u_id == ADMIN_ID: return True
    try:
        m = bot.get_chat_member(CANAL_ID, u_id)
        return m.status in ['member', 'administrator', 'creator']
    except: return False

@bot.message_handler(commands=['start'])
def start(msg):
    u_id = msg.from_user.id
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 OBTENIR UN SIGNAL")
    bot.send_message(msg.chat.id, f"🔥 **Bienvenue {msg.from_user.first_name} !**", reply_markup=markup, parse_mode='Markdown')

# --- ACTION: SIGNAL ---
@bot.message_handler(func=lambda m: m.text == "🚀 OBTENIR UN SIGNAL")
def get_signal(msg):
    u_id = msg.from_user.id
    now = datetime.now()

    if not check_sub(u_id):
        bot.send_message(msg.chat.id, "❌ Rejoins le canal @mexicain225officiel d'abord !")
        return

    # L'Admin et les VIP ne sont pas limités
    count = user_counts.get(u_id, 0)
    if u_id != ADMIN_ID and u_id not in vip_users and count >= 3:
        bot.send_message(msg.chat.id, "🚫 **LIMITE ATTEINTE**\n\nInscris-toi avec le code `COK225`, fais un dépôt et envoie ton ID ici pour devenir VIP illimité !")
        return

    # Simulation visuelle (Barre de chargement)
    status = bot.send_message(msg.chat.id, "⏳ `[▒▒▒▒▒▒▒▒▒▒] 15%`", parse_mode='Markdown')
    time.sleep(2)
    bot.edit_message_text("⏳ `[██████▒▒▒▒] 65%`", msg.chat.id, status.message_id, parse_mode='Markdown')
    time.sleep(2)
    bot.edit_message_text("✅ `[██████████] 100%`", msg.chat.id, status.message_id, parse_mode='Markdown')
    time.sleep(1)
    bot.delete_message(msg.chat.id, status.message_id)

    # Calcul temps (Décalage 5-7 min)
    delay = random.randint(5, 7)
    start_time = now + timedelta(minutes=delay)
    time_range = f"{start_time.strftime('%H:%M')} - {(start_time + timedelta(minutes=2)).strftime('%H:%M')}"
    
    # Cotes Élevées
    cote = random.randint(30, 150)
    prevision = random.randint(10, 25)
    
    # Mise à jour compteur
    if u_id != ADMIN_ID and u_id not in vip_users:
        user_counts[u_id] = count + 1
        with open(USAGE_FILE, "a") as f: f.write(f"{u_id}:{user_counts[u_id]}\n")

    # Format Exact Demandé
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

    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("📍 CLIQUE ICI POUR JOUER", url=LIEN_INSCRIPTION))
    bot.send_video(msg.chat.id, ID_VIDEO_UNIQUE, caption=txt, reply_markup=kb, parse_mode='Markdown')

# --- ADMINISTRATION ---
@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text) > 5)
def handle_id_submission(msg):
    u_id = msg.from_user.id
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("✅ VALIDER VIP", callback_data=f"val_{u_id}"))
    bot.send_message(ADMIN_ID, f"🔔 **NOUVEL ID REÇU**\nUser: {msg.from_user.first_name}\nID: `{msg.text}`", reply_markup=kb, parse_mode='Markdown')
    bot.send_message(msg.chat.id, "⏳ ID reçu. Activation en cours par l'administrateur...")

@bot.callback_query_handler(func=lambda c: c.data.startswith("val_"))
def admin_confirm(c):
    target_id = int(c.data.split("_")[1])
    if target_id not in vip_users:
        vip_users.add(target_id)
        save_user(DB_FILE, target_id)
        bot.send_message(target_id, "🌟 **ACCÈS VIP ACTIVÉ !**\nTu es maintenant en mode illimité. Profites-en !")
    bot.edit_message_text(f"✅ Utilisateur {target_id} validé !", ADMIN_ID, c.message.message_id)

if __name__ == "__main__":
    @app.route('/')
    def home(): return "Bot en ligne", 200
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
