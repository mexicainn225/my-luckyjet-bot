# ... (Gardez tout le début du code précédent identique) ...

@bot.message_handler(func=lambda m: m.text == "🚀 OBTENIR UN SIGNAL")
def check_signal(msg):
    u_id = msg.from_user.id
    user_data = get_user(u_id)

    if u_id == ADMIN_ID or user_data['is_vip']:
        status = bot.send_message(msg.chat.id, "⏳ `SYNCHRONISATION...`")
        time.sleep(1.5)
        bot.delete_message(msg.chat.id, status.message_id)
        
        # SIGNAL ACTUEL
        start_time, cote, prev = get_universal_signal()
        end_time = start_time + timedelta(minutes=2)
        
        # SIGNAL FUTUR (Le Double : +7 minutes après l'actuel)
        next_start = start_time + timedelta(minutes=7)
        next_end = next_start + timedelta(minutes=2)

        txt = (
            f"🚀 **SIGNAL VIP ACTIVÉ** 🧨\n\n"
            f"✅ **SIGNAL ACTUEL**\n"
            f"⚡️ **TIME** : `{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}`\n"
            f"⚡️ **CÔTE** : `{cote}X+` \n"
            f"⚡️ **PRÉVISION** : `{prev}X+` \n\n"
            f"🔜 **PROCHAIN SIGNAL (PRÉVISION)**\n"
            f"⌚️ **HEURE** : `{next_start.strftime('%H:%M')} - {next_end.strftime('%H:%M')}`\n\n"
            f"📍 **[CLIQUE ICI POUR JOUER]({LIEN_INSCRIPTION})**"
        )
        bot.send_message(msg.chat.id, txt, parse_mode='Markdown', disable_web_page_preview=True)
    else:
        # ... (Reste du code pour les non-VIP identique) ...
