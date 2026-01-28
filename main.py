import telebot, random, os, threading, time
from datetime import datetime, timedelta
from flask import Flask

app = Flask(__name__)
API_TOKEN = '8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0'
ADMIN_ID = 5724620019  
bot = telebot.TeleBot(API_TOKEN)

CANAL_ID, LIEN_INSCRIPTION, CODE_PROMO = "@mexicain225officiel", "https://lkbb.cc/e2d8", "COK225"
CONTACT_ADMIN, ID_VIDEO_UNIQUE = "@MEXICAINN225", "https://t.me/gagnantpro1xbet/138958" 

DB_FILE = "validated_users.txt"
def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return set(int(l.strip()) for l in f if l.strip().isdigit())
    return set()

def save_user(u_id):
    validated_users.add(u_id)
    with open(DB_FILE, "a") as f: f.write(f"{u_id}\n")

validated_users, user_signals_count, last_signal_expiry = load_users(), {}, {}

@app.route('/')
def health(): return "OK", 200

def check_sub(u_id):
    if u_id == ADMIN_ID: return True
    try:
        m = bot.get_chat_member(CANAL_ID, u_id)
        return m.status in ['member', 'administrator', 'creator']
    except: return False

def main_menu(u_id):
    m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add("🚀 OBTENIR UN SIGNAL")
    if u_id in validated_users or u_id == ADMIN_ID: m.add("👑 SIGNAL PREMIUM 👑")
    return m

@bot.message_handler(commands=['start'])
def start(msg):
    u_id = msg.from_user.id
    if not check_sub(u_id):
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("📢 Rejoindre", url=f"https://t.me/{CANAL_ID[1:]}"))
        bot.send_message(msg.chat.id, "❌ Rejoins le canal pour activer.", reply_markup=kb)
        return
    bot.send_message(msg.chat.id, "✅ ACCÈS VALIDÉ", reply_markup=main_menu(u_id))

@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text) > 5)
def handle_id(msg):
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("✅ Valider", callback_data=f"ok_{msg.from_user.id}"))
    bot.send_message(ADMIN_ID, f"🔔 ID: {msg.text}\nNom: {msg.from_user.first_name}", reply_markup=kb)
    bot.send_message(msg.chat.id, "⏳ En attente de validation par l'admin...")

@bot.callback_query_handler(func=lambda c: c.data.startswith("ok_"))
def valider(c):
    u_id = int(c.data.split("_")[1])
    save_user(u_id)
    bot.send_message(u_id, "🎉 Validé ! Profite du PREMIUM.", reply_markup=main_menu(u_id))
    bot.edit_message_text(f"✅ Utilisateur {u_id} validé !", ADMIN_ID, c.message.message_id)

@bot.message_handler(func=lambda m: m.text in ["🚀 OBTENIR UN SIGNAL", "👑 SIGNAL PREMIUM 👑"])
def signal(msg):
    u_id, now = msg.from_user.id, datetime.now()
    if u_id in last_signal_expiry and now < last_signal_expiry[u_id]:
        d = last_signal_expiry[u_id] - now
        bot.reply_to(msg, f"⏳ Attends {int(d.total_seconds()//60)}m {int(d.total_seconds()%60)}s.")
        return
    if not check_sub(u_id): return
    
    count = user_signals_count.get(u_id, 0)
    if u_id != ADMIN_ID and u_id not in validated_users and count >= 3:
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("🎁 S'INSCRIRE", url=LIEN_INSCRIPTION))
        bot.send_message(msg.chat.id, "🔒 Limite atteinte. Inscris-toi pour continuer.", reply_markup=kb)
        return

    start_dt = now + timedelta(minutes=random.randint(3,6))
    end_dt = start_dt + timedelta(minutes=2)
    last_signal_expiry[u_id] = end_dt
    
    if "PREMIUM" in msg.text:
        c, p, a = random.randint(50,200), random.randint(20,45), random.randint(8,15)
        txt = f"👑 **PREMIUM**\n⌚ {start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}\n📈 {c}X+\n🎯 {p}X+\n🛡 {a}X+"
    else:
        user_signals_count[u_id] = count + 1
        c, p, a = random.randint(3,60), random.randint(10,25), random.randint(2,7)
        txt = f"🚀 **SIGNAL**\n⌚ {start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}\n📈 {c}X+\n🎯 {p}X+\n🛡 {a}X+"

    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("📲 JOUER", url=LIEN_INSCRIPTION))
    bot.send_video(msg.chat.id, ID_VIDEO_UNIQUE, caption=txt, reply_markup=kb, parse_mode='Markdown')

if __name__ == "__main__":
    bot.remove_webhook()
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
