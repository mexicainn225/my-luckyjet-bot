def get_universal_signal():
    now = datetime.now()
    base_minute = get_base_minute()
    
    # 1. On calcule le nombre total de minutes depuis MINUIT (00:00)
    # Cela permet de garder le cycle de 14min fluide entre deux heures.
    total_minutes_now = now.hour * 60 + now.minute
    
    # 2. On définit le point de départ (en minutes depuis minuit)
    start_point = base_minute 
    
    # 3. On cherche le prochain créneau de 14 minutes
    # (Ex: si base=23, les créneaux sont 23, 37, 51, 65, 79...)
    next_sig_total = start_point
    while next_sig_total <= total_minutes_now:
        next_sig_total += 14 # Ton cycle de 14 minutes
        
    # 4. On convertit ces minutes totales en Heure:Minute réelle
    target_hour = (next_sig_total // 60) % 24
    target_minute = next_sig_total % 60
    
    start_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    # 5. On utilise ce timestamp unique pour générer la côte
    random.seed(start_time.timestamp()) 
    cote = random.randint(30, 150)
    prev = random.randint(10, 25)
    random.seed() 
    
    return start_time, cote, prev
