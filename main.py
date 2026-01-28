import telebot, random, os, threading, time
from datetime import datetime, timedelta
from flask import Flask

app = Flask(__name__)

# --- CONFIGURATION ---
# Ton token est maintenant intégré ici
API_TOKEN = '8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0' 
ADMIN_ID = 5724620019  
bot = telebot.TeleBot(API_TOKEN)

CANAL_ID = "@mexicain225officiel"
LIEN_INSCRIPTION = "https://lkbb.cc/e2d8"
CODE_PROMO = "COK225"
ID_VIDEO_UNIQUE = "https://t.me/gagnantpro1xbet/138958" 

DB_FILE = "validated_users.txt"
USAGE_FILE = "usage_stats.txt"

# --- PERSISTENCE DES DONNÉES ---
def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: 
            return set(int(l.strip()) for l in f if l.strip().isdigit())
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

# --- FONCTIONS SYSTÈME ---
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

# --- COMMANDES PRINCIPALES ---
@bot.message_handler(commands=['start'])
def start(msg):
    u_id = msg.from_user.id
    if not check_sub(u_id):
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("📢 Rejoindre le Canal", url=f"https://t.me/{CANAL_ID[1:]}"))
        bot.send_message(msg.chat.id, "❌ **ACCÈS REFUSÉ**\n\nRejoins le canal d'abord pour débloquer le bot !", reply_markup=kb, parse_mode='Markdown')
        return
    bot.send_message(msg.chat.id, f"🔥 **Bienvenue {msg.from_user.first_name} !**\nPrêt à encaisser avec l'Analyseur ?", reply_markup=main_menu(u_id), parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "📊 STATS ADMIN" and m.from_user.id == ADMIN_ID)
def admin_stats(msg):
    bot.send_message(ADMIN_ID, f"📈 **STATS ADMIN**\n\nVIP Validés : `{len(validated_users)}`", parse_mode='Markdown')

# --- LOGIQUE DE GÉNÉRATION DES SIGNAUX ---
@bot.message_handler(func=lambda m: m.text in ["🚀 OBTENIR UN SIGNAL", "👑 SIGNAL PREMIUM 👑"])
def handle_signals(msg):
    u_id = msg.from_user.id
    is_premium = "PREMIUM" in msg.text
    now = datetime.now()

    # Vérification anti-spam (Signal précédent doit être terminé)
    if u_id in last_signal_end_time and now < last_signal_end_time[u_id]:
        diff = last_signal_end_time[u_id] - now
        mins, secs = divmod(int(diff.total_seconds()), 60)
        bot.reply_to(msg, f"⏳ **VEUILLEZ PATIENTER**\nLe signal précédent est encore valide.\nProchain disponible dans : `{mins}m {secs}s`.", parse_mode='Markdown')
        return

    # Vérification Accès Premium
    if is_premium and u_id not in validated_users and u_id != ADMIN_ID:
        bot.reply_to(msg, "⛔ **ACCÈS VIP REQUIS**\n\nInscris-toi avec le code **COK225** et envoie ton ID ici pour validation.")
        return

    # Limite gratuit (3 signaux max à vie)
    count = user_signals_count.get(u_id, 0)
    if not is_premium and u_id not in validated_users and u_id != ADMIN_ID and count >= 3:
        bot.send_message(msg.chat.id, f"🚫 **LIMITE ATTEINTE**\n\nTes 3 signaux gratuits sont terminés.\nCrée un compte avec le code `{CODE_PROMO}` pour passer en Premium illimité !", parse_mode='Markdown')
        return

    # --- CALCUL DU DÉCALAGE (5 à 7 min dans le futur) ---
    delay = random.randint(5, 7) 
    start_time = now + timedelta(minutes=delay)
    
    # L'utilisateur est bloqué pour 6 minutes après l'appui
    last_signal_end_time[u_id] = now + timedelta(minutes=6)

    if is_premium:
        # Cotes Premium (min 10)
        cote = f"{random.randint(10, 300)}X+"
        prevision = f"{random.randint(10, 50)}X+"
        assurance = f"{random.randint(2, 10)}X+"
        
        # Format temps Premium (intervalle de 2 min)
        end_time_display = start_time + timedelta(minutes=2)
        time_range = f"{start_time.strftime('%H:%M')} - {end_time_display.strftime('%H:%M')}"
        
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
        # Cotes Standard (min 4)
        user_signals_count[u_id] = count + 1
        save_usage(u_id, count + 1)
        
        cote = f"{random.randint(4, 30)}X+"
        assurance = f"{random.randint(1, 5)}X+"
        
        # Format temps Standard (intervalle de 1 min)
        end_time_display = start_time + timedelta(minutes=1)
        time_range = f"{start_time.strftime('%H:%M')} - {end_time_display.strftime('%H:%M')}"
        
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

# --- VALIDATION VIP ---
@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text) > 5)
def register_id(msg):
    u_id = msg.from_user.id
    if u_id in validated_users:
        bot.send_message(msg.chat.id, "✅ Tu es déjà membre Premium.")
        return
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("✅ CONFIRMER PREMIUM", callback_data=f"vip_{u_id}"))
    bot.send_message(ADMIN_ID, f"🔔 **NOUVEAU CANDIDAT PREMIUM**\n\nUser: {msg.from_user.first_name}\nID 1xBet: `{msg.text}`", reply_markup=kb, parse_mode='Markdown')
    bot.send_message(msg.chat.id, "⏳ **VÉRIFICATION...**\nTon ID est en cours d'examen par l'administrateur. Tu seras notifié dès l'activation.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("vip_"))
def confirm_vip(c):
    target_id = int(c.data.split("_")[1])
    if target_id not in validated_users:
        validated_users.add(target_id)
        with open(DB_FILE, "a") as f: f.write(f"{target_id}\n")
        try:
            bot.send_message(target_id, "🌟 **PREMIUM ACTIVÉ !**\n\nFélicitations, tu as maintenant accès aux signaux VIP illimités.", reply_markup=main_menu(target_id))
        except: pass
    bot.edit_message_text(f"✅ Utilisateur {target_id} validé !", ADMIN_ID, c.message.message_id)

# --- LANCEMENT ---
if __name__ == "__main__":
    @app.route('/')
    def home(): return "Bot Online", 200
    
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
