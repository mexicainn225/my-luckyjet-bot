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
USAGE_FILE = "usage_stats.txt" # Fichier pour les 3 signaux gratuits

# --- CHARGEMENT DES DONNÉES ---

def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: 
            return set(int(l.strip()) for l in f if l.strip().isdigit())
    return set()

def load_usage():
    """Charge le nombre de signaux utilisés par chaque utilisateur"""
    usage = {}
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            for line in f:
                if ":" in line:
                    u_id, count = line.strip().split(":")
                    usage[int(u_id)] = int(count)
    return usage

def save_usage(u_id, count):
    """Sauvegarde le nouveau compteur dans le fichier"""
    usage_data = load_usage()
    usage_data[u_id] = count
    with open(USAGE_FILE, "w") as f:
        for uid, c in usage_data.items():
            f.write(f"{uid}:{c}\n")

def save_user(u_id):
    validated_users.add(u_id)
    with open(DB_FILE, "a") as f: f.write(f"{u_id}\n")

# Initialisation des données
validated_users = load_users()
user_signals_count = load_usage() # On charge depuis le fichier ici
last_signal_expiry = {}

# --- FONCTIONS DU BOT ---

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
        markup.add(telebot.types.KeyboardButton("👑 SIGNAL PREMIUM VIP 👑"))
    if u_id == ADMIN_ID:
        markup.add(telebot.types.KeyboardButton("📊 STATS ADMIN"))
    return markup

@bot.message_handler(commands=['start'])
def start(msg):
    u_id = msg.from_user.id
    if not check_sub(u_id):
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("📢 Rejoindre le Canal", url=f"https://t.me/{CANAL_ID[1:]}"))
        bot.send_message(msg.chat.id, "⚠️ **ACCÈS RESTREINT**\n\nRejoins le canal d'abord !", reply_markup=kb, parse_mode='Markdown')
        return
    bot.send_message(msg.chat.id, f"👋 **Bonjour {msg.from_user.first_name} !**", reply_markup=main_menu(u_id), parse_mode='Markdown')

# --- LOGIQUE DE SIGNAL ---

@bot.message_handler(func=lambda m: m.text in ["🚀 OBTENIR UN SIGNAL", "👑 SIGNAL PREMIUM VIP 👑"])
def send_signal(msg):
    u_id = msg.from_user.id
    is_premium = "PREMIUM" in msg.text
    now = datetime.now()

    # 1. Vérification Anti-Spam
    if u_id in last_signal_expiry and now < last_signal_expiry[u_id]:
        diff = last_signal_expiry[u_id] - now
        bot.reply_to(msg, f"⏳ Attends `{int(diff.total_seconds())}s` avant la prochaine analyse.")
        return

    # 2. Vérification Accès Premium
    if is_premium and u_id not in validated_users and u_id != ADMIN_ID:
        bot.reply_to(msg, "❌ **ACCÈS PREMIUM REQUIS**\n\nInscris-toi avec le code **COK225** pour débloquer cette option.")
        return

    # 3. Vérification Limite Gratuit (PERSISTANTE)
    count = user_signals_count.get(u_id, 0)
    if not is_premium and u_id not in validated_users and u_id != ADMIN_ID:
        if count >= 3:
            kb = telebot.types.InlineKeyboardMarkup()
            kb.add(telebot.types.InlineKeyboardButton("🎁 S'INSCRIRE MAINTENANT", url=LIEN_INSCRIPTION))
            bot.send_message(msg.chat.id, f"🚫 **LIMITE DE 3 SIGNAUX ATTEINTE**\n\nPour continuer à gagner, crée un compte avec le code `{CODE_PROMO}` et envoie ton ID ici !", reply_markup=kb, parse_mode='Markdown')
            return
        
        # On incrémente et on SAUVEGARDE dans le fichier
        new_count = count + 1
        user_signals_count[u_id] = new_count
        save_usage(u_id, new_count)

    # 4. Génération du signal (Design stylé)
    wait = random.randint(1, 3)
    start_dt = now + timedelta(minutes=wait)
    time_str = start_dt.strftime('%H:%M')

    if is_premium:
        c = round(random.uniform(10.0, 100.0), 2)
        txt = (
            f"👑 **SIGNAL VIP PREMIUM** 👑\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏰ **HEURE** : `{time_str}`\n"
            f"🎯 **CÔTE VISÉE** : `{c}x` \n"
            f"🔥 **CONFIANCE** : `99%` \n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💎 *Exclusivité Membres Premium*"
        )
    else:
        c = round(random.uniform(1.5, 4.0), 2)
        txt = (
            f"🚀 **SIGNAL STANDARD** ({count+1}/3)\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏰ **HEURE** : `{time_str}`\n"
            f"📈 **CÔTE** : `{c}x` \n"
            f"🛡 **SÉCURITÉ** : `85%` \n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎁 Code : `{CODE_PROMO}`"
        )

    last_signal_expiry[u_id] = now + timedelta(seconds=60) # 1 min de pause entre les signaux
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("📲 PLACER MON PARI", url=LIEN_INSCRIPTION))
    bot.send_video(msg.chat.id, ID_VIDEO_UNIQUE, caption=txt, reply_markup=kb, parse_mode='Markdown')

# --- GESTION DES IDS (VALIDATION ADMIN) ---

@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text) > 5)
def handle_id(msg):
    u_id = msg.from_user.id
    if u_id in validated_users:
        bot.send_message(msg.chat.id, "✅ Tu es déjà validé !")
        return
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("✅ VALIDER VIP", callback_data=f"ok_{u_id}"))
    bot.send_message(ADMIN_ID, f"🔔 **DEMANDE VIP**\nUser: {msg.from_user.first_name}\nID: `{msg.text}`", reply_markup=kb, parse_mode='Markdown')
    bot.send_message(msg.chat.id, "⏳ Ton ID est en cours de vérification par l'admin...")

@bot.callback_query_handler(func=lambda c: c.data.startswith("ok_"))
def admin_confirm(c):
    u_id = int(c.data.split("_")[1])
    save_user(u_id)
    bot.send_message(u_id, "🌟 **BRAVO !** Ton accès Premium est activé !", reply_markup=main_menu(u_id))
    bot.edit_message_text(f"✅ User {u_id} validé !", ADMIN_ID, c.message.message_id)

if __name__ == "__main__":
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
