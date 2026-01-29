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
def get_base_minute():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            val = f.read().strip()
            return int(val) if val.isdigit() else 23
    return 23

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return set(int(l.strip()) for l in f if l.strip().isdigit())
    return set()

vip_users = load_db()
user_counts = {}

# --- LOGIQUE SYNCHRONISÉE ---
def get_universal_signal():
    now = datetime.now()
    base_minute = get_base_minute()
    current_total = now.hour * 60 + now.minute
    base_total = now.hour * 60 + base_minute
    if current_total < base_total: base_total -= 60
    next_mins = base_total
    while next_mins <= current_total: next_mins += 7
    start_time = now.replace(hour=(next_mins // 60) % 24, minute=next_mins % 60, second=0, microsecond=0)
    
    random.seed(start_time.timestamp()) 
    cote, prev, assurance = random.randint(30, 150), random.randint(10, 25), random.randint(3, 9)
    random.seed() 
    return start_time, cote, prev, assurance

# --- ANIMATION D'IMPRESSION (L'ÉTAPE QUI CHARGE) ---
def impressive_loading(chat_id):
    steps = [
        "🔍 `Connexion aux serveurs 1xBet...`",
        "📡 `Extraction de l'algorithme de hachage...`",
        "🧠 `Analyse de la tendance (Stratégie 7min)...`",
        "⚖️ `Calcul de la probabilité de succès : 98.4%`",
        "🚀 `GÉNÉRATION DU SIGNAL GAGNANT...`"
    ]
    
    sent_msg = bot.send_message(chat_id, steps[0], parse_mode='Markdown')
    for step in steps[1:]:
        time.sleep(1.5) # Délai pour laisser l'utilisateur lire
        bot.edit_message_text(step, chat_id, sent_msg.message_id, parse_mode='Markdown')
    
    time.sleep(1)
    bot.delete_message(chat_id, sent_msg.message_id)

# --- ACTIONS ---
@bot.message_handler(commands=['start'])
def start(msg):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 OBTENIR UN SIGNAL", "📊 STATS DU JOUR")
    bot.send_message(msg.chat.id, f"🔥 **Système MEXICAIN225 Actif**\nPrécision actuelle : 98%\n\nCliquez sur le bouton pour analyser.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 OBTENIR UN SIGNAL")
def handle_signal(msg):
    u_id = msg.from_user.id
    count = user_counts.get(u_id, 0)
    
    if u_id != ADMIN_ID and u_id not in vip_users and count >= 3:
        bot.send_message(msg.chat.id, "🚫 **LIMITE QUOTIDIENNE ATTEINTE**\n\nInscris-toi avec le code `COK225` et valide ton ID pour débloquer l'IA à vie.")
        return

    # LANCEMENT DE L'ANIMATION QUI IMPRESSIONNE
    impressive_loading(msg.chat.id)

    # Récupération des données
    start_time, cote, prevision, assurance = get_universal_signal()
    time_range = f"{start_time.strftime('%H:%M')} - {(start_time + timedelta(minutes=2)).strftime('%H:%M')}"
    if u_id != ADMIN_ID and u_id not in vip_users: user_counts[u_id] = count + 1

    txt = (
        f"✅ **SIGNAL ANALYSÉ AVEC SUCCÈS** 🧨\n\n"
        f"⚡️ **JEU** : `AVIATRIX / LUCKYJET`\n"
        f"⚡️ **TIME** : `{time_range}`\n"
        f"⚡️ **CÔTE** : `{cote}X+` \n"
        f"⚡️ **PRÉVISION** : `{prevision}X+` \n"
        f"⚡️ **ASSURANCE** : `{assurance}.50X+` \n\n"
        f"📍 [CLIQUE ICI POUR JOUER]({LIEN_INSCRIPTION})\n"
        f"🎁 **CODE PROMO** : `{CODE_PROMO}`"
    )
    kb = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("📍 JOUER MAINTENANT", url=LIEN_INSCRIPTION))
    bot.send_video(msg.chat.id, ID_VIDEO_UNIQUE, caption=txt, reply_markup=kb, parse_mode='Markdown')

# --- COMMANDES ADMIN ---
@bot.message_handler(commands=['minute'])
def change_minute(msg):
    if msg.from_user.id == ADMIN_ID:
        try:
            val = msg.text.split()[1]
            with open(CONFIG_FILE, "w") as f: f.write(val)
            bot.send_message(ADMIN_ID, f"✅ Stratégie recalibrée sur la minute `{val}`")
        except: pass

@bot.callback_query_handler(func=lambda c: c.data.startswith("val_"))
def val(c):
    uid = int(c.data.split("_")[1])
    vip_users.add(uid)
    with open(DB_FILE, "a") as f: f.write(f"{uid}\n")
    bot.send_message(uid, "🌟 **IA DÉBLOQUÉE !**\nTu as maintenant un accès illimité aux signaux.")
    bot.edit_message_text("✅ Utilisateur validé !", ADMIN_ID, c.message.message_id)

@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text) > 5)
def handle_id(msg):
    kb = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("✅ VALIDER VIP", callback_data=f"val_{msg.from_user.id}"))
    bot.send_message(ADMIN_ID, f"🔔 **NOUVEL ID** : `{msg.text}`", reply_markup=kb)
    bot.send_message(msg.chat.id, "⏳ Analyse de votre ID par le serveur...")

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    def run_bot():
        while True:
            try: bot.infinity_polling(timeout=20)
            except: time.sleep(5)
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
