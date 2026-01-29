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

CONFIG_FILE = "base_minute.txt"

# --- PERSISTENCE ---
def get_base_minute():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            val = f.read().strip()
            return int(val) if val.isdigit() else 23
    return 23

# --- LOGIQUE DE SYNCHRONISATION (RÉSULTAT UNIQUE) ---
def get_universal_signal():
    now = datetime.now()
    base_minute = get_base_minute()
    
    current_total_mins = now.hour * 60 + now.minute
    base_total_mins = now.hour * 60 + base_minute
    
    if current_total_mins < base_total_mins:
        base_total_mins -= 60

    next_signal_mins = base_total_mins
    while next_signal_mins <= current_total_mins:
        next_signal_mins += 7
        
    start_time = now.replace(hour=(next_signal_mins // 60) % 24, minute=next_signal_mins % 60, second=0, microsecond=0)
    
    # --- LA MAGIE ICI ---
    # On utilise l'heure du signal comme "graine" pour le hasard
    # Ainsi, pour un même start_time, random donnera toujours le même chiffre
    random.seed(start_time.timestamp()) 
    
    cote = random.randint(30, 150)
    prevision = random.randint(10, 25)
    
    # On réinitialise le hasard pour ne pas perturber le reste du bot
    random.seed() 
    
    return start_time, cote, prevision

# --- ACTIONS ---
@bot.message_handler(func=lambda m: m.text == "🚀 OBTENIR UN SIGNAL")
def get_signal(msg):
    u_id = msg.from_user.id
    
    # Simulation de calcul
    status = bot.send_message(msg.chat.id, "⏳ `SYNCHRONISATION AVEC LE SERVEUR...`")
    time.sleep(2)
    bot.delete_message(msg.chat.id, status.message_id)

    # Récupération du signal unique pour tout le monde
    start_time, cote, prevision = get_universal_signal()
    
    end_time_display = start_time + timedelta(minutes=2)
    time_range = f"{start_time.strftime('%H:%M')} - {end_time_display.strftime('%H:%M')}"

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

# --- COMMANDE CONFIG ADMIN ---
@bot.message_handler(commands=['config'])
def config_minute(msg):
    if msg.from_user.id == ADMIN_ID:
        try:
            new_min = int(msg.text.split()[1])
            with open(CONFIG_FILE, "w") as f: f.write(str(new_min))
            bot.send_message(ADMIN_ID, f"✅ Nouvelle base : minute `{new_min}`. Tous les signaux mondiaux sont synchronisés sur cette base + 7min.")
        except:
            bot.send_message(ADMIN_ID, "❌ Utilise : `/config 23`")

if __name__ == "__main__":
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
    def home(): return "Bot en ligne", 200
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
