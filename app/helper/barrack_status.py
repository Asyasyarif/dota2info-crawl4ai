def parse_barracks_status(status: int) -> str:
    barracks = [
        "Melee Top", "Ranged Top",
        "Melee Middle", "Ranged Middle",
        "Melee Bottom", "Ranged Bottom"
    ]
    
    status_binary = format(status, '06b')
    
    destroyed_barracks = [barracks[i] for i in range(6) if status_binary[5 - i] == '0']
    
    if not destroyed_barracks:
        return "All barracks are intact."
    
    return "Destroyed: " + ", ".join(destroyed_barracks)