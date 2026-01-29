import telebot, random, os, threading, time, requests
from datetime import datetime, timedelta
from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)

# --- CONFIGURATION ---
API_TOKEN = '8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0' 
ADMIN_ID = 5724620019  
# Ton lien MongoDB injecté ici :
MONGO_URI = "mongodb+srv://mexicain225:03191967@cluster0.zmj8ocq.mongodb.net/" 

bot = telebot.TeleBot(API_TOKEN)
client = MongoClient(MONGO_URI)
db = client['luckyjet_db']
users_col = db['users'] 
config_col = db['config']

# --- FONCTIONS DATABASE ---
def get_user_status(u_id):
    user = users_col.find_one({"_id": u_id})
    if not user:
        # On crée l'utilisateur avec is_vip = False par défaut
        users_col.insert_one({"_id": u_id, "is_vip": False})
        return False
    return user.get("is_vip", False)

def get_base_minute():
    conf = config_col.find_one({"_id": "settings"})
    return conf['minute'] if conf else 23

# --- LOGIQUE DE SIGNAL (SYNCHRONISÉ TOUTES LES 7 MIN) ---
def get_universal_signal():
    now = datetime.now()
    base_minute = get_base_minute()
    current_total = now.hour * 60 + now.minute
    base_total = now.hour * 60 + base_minute
    if current_total < base_total: base_total -= 60
    
    next_sig = base_total
    while next_sig <= current_total: next_sig += 7
    
    start_time = now.replace(hour=(next_sig // 60) % 24, minute=next_sig % 60, second=0, microsecond=0)
    random.seed(start_time.timestamp()) 
    cote = round(random.uniform(2.0, 15.0), 2)
    prev = round(random.uniform(1.5, 4.0), 2)
    random.seed() 
    return start_time, cote, prev

# --- COMMANDES ---
@bot.message_handler(commands=['start'])
def start(msg):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 OBTENIR UN SIGNAL")
    bot.send_message(msg.chat.id, f"🔥 **Bienvenue {msg.from_user.first_name} !**\n\nPour accéder aux signaux de la faille Mexicaine, tu dois posséder un compte certifié avec le code promo **COK225**.", reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "🚀 OBTENIR UN SIGNAL")
def handle_signal_request(msg):
    u_id = msg.from_user.id
    is_vip = get_user_status(u_id)

    # Si l'utilisateur n'est pas VIP et n'est pas l'ADMIN
    if u_id != ADMIN_ID and not is_vip:
        txt_verif = (
            "⚠️ **ACCÈS REFUSÉ** ⚠️\n\n"
            "Ton compte n'est pas encore activé dans notre base de données.\n\n"
            "**ÉTAPE D'ACTIVATION :**\n"
            "1️⃣ Inscris-toi ici : [CLIQUE ICI](https://lkbb.cc/e2d8)\n"
            "2️⃣ Utilise le code promo : `COK225`\n"
            "3️⃣ Effectue un dépôt sur ton compte.\n"
            "4️⃣ **Envoie ton ID de joueur ici** pour validation."
        )
        bot.send_message(msg.chat.id, txt_verif, parse_mode='Markdown', disable_web_page_preview=True)
        return

    # Si VIP ou ADMIN
    status = bot.send_message(msg.chat.id, "⏳ `VÉRIFICATION... OK`")
    time.sleep(1.5)
    bot.edit_message_text("⏳ `SYNCHRONISATION FAILLE...`", msg.chat.id, status.message_id)
    time.sleep(1.5)
    bot.delete_message(msg.chat.id, status.message_id)

    start_time, cote, prev = get_universal_signal()
    end_time = start_time + timedelta(minutes=2)

    final_txt = (
        f"🚀 **SIGNAL MEXICAIN225** 🧨\n\n"
        f"⚡️ **TIME** : `{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}`\n"
        f"⚡️ **CÔTE** : `{cote}X+` \n"
        f"⚡️ **PRÉVISION** : `{prev}X+` \n"
        f"⚡️ **ASSURANCE** : `2.50X+` \n\n"
        f"📍 **CLIQUE ICI POUR JOUER**\n"
        f"🎁 **CODE PROMO** : `COK225`"
    )
    kb = telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("📍 JOUER", url="https://lkbb.cc/e2d8"))
    
    # Utilisation d'un message avec photo ou texte si la vidéo ne charge pas
    bot.send_message(msg.chat.id, final_txt, reply_markup=kb, parse_mode='Markdown')

# --- VALIDATION ADMIN ---
@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text) >= 7)
def check_id_submission(msg):
    kb = telebot.types.InlineKeyboardMarkup().add(
        telebot.types.InlineKeyboardButton("✅ ACTIVER VIP", callback_data=f"activate_{msg.from_user.id}")
    )
    bot.send_message(ADMIN_ID, f"🔔 **NOUVEL ID À VÉRIFIER**\nUser: {msg.from_user.first_name}\nID: `{msg.text}`", reply_markup=kb, parse_mode='Markdown')
    bot.send_message(msg.chat.id, "📡 **ID reçu.** Un administrateur vérifie ton compte. Tu recevras une notification dès validation.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("activate_"))
def admin_activation(c):
    target_id = int(c.data.split("_")[1])
    users_col.update_one({"_id": target_id}, {"$set": {"is_vip": True}}, upsert=True)
    bot.send_message(target_id, "🌟 **FÉLICITATIONS !**\n\nTon compte a été vérifié. Tu as désormais un accès **ILLIMITÉ** aux signaux.")
    bot.edit_message_text(f"✅ Utilisateur {target_id} activé !", ADMIN_ID, c.message.message_id)

@bot.message_handler(commands=['config'])
def admin_config(msg):
    if msg.from_user.id == ADMIN_ID:
        try:
            new_min = int(msg.text.split()[1])
            config_col.update_one({"_id": "settings"}, {"$set": {"minute": new_min}}, upsert=True)
            bot.send_message(ADMIN_ID, f"✅ Cycle synchronisé sur la minute `{new_min}`")
        except:
            bot.send_message(ADMIN_ID, "❌ Format: /config 23")

if __name__ == "__main__":
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
