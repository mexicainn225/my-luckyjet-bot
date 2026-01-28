import telebot, random, os, threading, time
from datetime import datetime, timedelta
from flask import Flask

app = Flask(__name__)

# --- CONFIGURATION ---
API_TOKEN = '8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0' 
bot = telebot.TeleBot(API_TOKEN)

CANAL_ID = "@mexicain225officiel"
LIEN_INSCRIPTION = "https://lkbb.cc/e2d8"
CODE_PROMO = "COK225"
ID_VIDEO_UNIQUE = "https://t.me/gagnantpro1xbet/138958" 

USAGE_FILE = "usage_stats.txt" # Fichier pour compter les jeux

# --- GESTION DU COMPTEUR (SAUVEGARDE) ---
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
        for uid, c in usage_data.items():
            f.write(f"{uid}:{c}\n")

user_signals_count = load_usage()
last_signal_end_time = {}

# --- FONCTIONS ---
def check_sub(u_id):
    try:
        m = bot.get_chat_member(CANAL_ID, u_id)
        return m.status in ['member', 'administrator', 'creator']
    except: return False

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(telebot.types.KeyboardButton("🚀 OBTENIR UN SIGNAL"))
    return markup

@bot.message_handler(commands=['start'])
def start(msg):
    u_id = msg.from_user.id
    if not check_sub(u_id):
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("📢 Rejoindre le Canal", url=f"https://t.me/{CANAL_ID[1:]}"))
        bot.send_message(msg.chat.id, "❌ **ACCÈS REFUSÉ**\n\nRejoins le canal d'abord !", reply_markup=kb, parse_mode='Markdown')
        return
    bot.send_message(msg.chat.id, f"🔥 **Bienvenue {msg.from_user.first_name} !**", reply_markup=main_menu(), parse_mode='Markdown')

# --- LOGIQUE DE SIGNAL AVEC LIMITE ---
@bot.message_handler(func=lambda m: m.text == "🚀 OBTENIR UN SIGNAL")
def signal_logic(msg):
    u_id = msg.from_user.id
    now = datetime.now()

    # 1. Vérification de l'abonnement au canal
    if not check_sub(u_id):
        bot.reply_to(msg, "❌ Tu dois être dans le canal pour recevoir des signaux.")
        return

    # 2. Vérification de la limite de 3 jeux (POINT DEMANDÉ)
    count = user_signals_count.get(u_id, 0)
    if count >= 3:
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("🎁 S'INSCRIRE (CODE: COK225)", url=LIEN_INSCRIPTION))
        bot.send_message(msg.chat.id, 
            f"🚫 **LIMITE GRATUITE ATTEINTE**\n\n"
            f"Tu as déjà utilisé tes 3 signaux gratuits.\n\n"
            f"Pour continuer à gagner, tu dois :\n"
            f"1️⃣ Créer un nouveau compte avec le code promo : `{CODE_PROMO}`\n"
            f"2️⃣ Faire un dépôt de 2000 F minimum.\n"
            f"3️⃣ Envoyer ton ID ici pour validation.", 
            reply_markup=kb, parse_mode='Markdown')
        return

    # 3. Vérification anti-spam (5-6 min)
    if u_id in last_signal_end_time and now < last_signal_end_time[u_id]:
        diff = last_signal_end_time[u_id] - now
        mins, secs = divmod(int(diff.total_seconds()), 60)
        bot.reply_to(msg, f"⏳ **ANALYSE EN COURS...**\nAttends `{mins}m {secs}s`.")
        return

    # --- GÉNÉRATION DU SIGNAL ---
    # Incrémenter et sauvegarder le compteur
    new_count = count + 1
    user_signals_count[u_id] = new_count
    save_usage(u_id, new_count)

    delay = random.randint(5, 7)
    start_time = now + timedelta(minutes=delay)
    end_time_display = start_time + timedelta(minutes=2)
    last_signal_end_time[u_id] = now + timedelta(minutes=6)

    cote = f"{random.randint(50, 150)}X+"
    prevision = f"{random.randint(10, 30)}X+"
    assurance = f"{random.randint(2, 5)}X+"
    time_range = f"{start_time.strftime('%H:%M')} - {end_time_display.strftime('%H:%M')}"
    
    txt = (
        f"🚀 **SIGNAL MEXICAIN225** 🧨\n"
        f"*(Signal gratuit {new_count}/3)*\n\n"
        f"⚡️ **TIME** : `{time_range}`\n"
        f"⚡️ **CÔTE** : `{cote}`\n"
        f"⚡️ **PRÉVISION** : `{prevision}`\n"
        f"⚡️ **ASSURANCE** : `{assurance}`\n\n"
        f"📍 **CLIQUE ICI POUR JOUER**\n"
        f"🎁 **CODE PROMO** : `{CODE_PROMO}`\n\n"
        f"👤 **CONTACT** : @MEXICAINN225"
    )

    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("📍 CLIQUE ICI POUR JOUER", url=LIEN_INSCRIPTION))
    
    bot.send_video(msg.chat.id, ID_VIDEO_UNIQUE, caption=txt, reply_markup=kb, parse_mode='Markdown')

# --- LANCEMENT ---
if __name__ == "__main__":
    @app.route('/')
    def home(): return "Bot Online", 200
    
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
