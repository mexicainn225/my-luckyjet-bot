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
CONFIG_FILE = "base_minute.txt"

# --- PERSISTENCE DES DONNÉES ---
def load_db(file):
    if os.path.exists(file):
        with open(file, "r") as f: return set(int(l.strip()) for l in f if l.strip().isdigit())
    return set()

def save_user(file, u_id):
    with open(file, "a") as f: f.write(f"{u_id}\n")

def get_base_minute():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            val = f.read().strip()
            return int(val) if val.isdigit() else 23
    return 23

vip_users = load_db(DB_FILE)
user_counts = {} # Simple dictionnaire pour la session

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
    
    # Seeding pour que tout le monde ait la même cote au même moment
    random.seed(start_time.timestamp()) 
    cote = random.randint(30, 150)
    prevision = random.randint(10, 25)
    random.seed() # Reset seed
    
    return start_time, cote, prevision

# --- COMMANDES ADMIN ---
@bot.message_handler(commands=['config'])
def config_minute(msg):
    if msg.from_user.id == ADMIN_ID:
        try:
