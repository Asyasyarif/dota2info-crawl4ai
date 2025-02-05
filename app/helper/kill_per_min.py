import math

def kills_per_min_text(kills_per_min: float) -> str:
    if kills_per_min <= 0:
        return "Tidak ada kill dalam pertandingan"
    
    kills_per_min = round(kills_per_min, 3)
    minutes_per_kill = 1 / kills_per_min if kills_per_min > 0 else float('inf')
    rounded_minutes = math.ceil(minutes_per_kill)
    
    if rounded_minutes == 1:
        return "Sekitar 1 kill setiap menit"
    else:
        return f"Sekitar 1 kill setiap {rounded_minutes} menit"