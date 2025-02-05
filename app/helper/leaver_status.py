def get_leaver_status_description(status_id: int) -> str:
    match status_id:
        case 0:
            return "finished match, no abandon"
        case 1:
            return "player DC, no abandon"
        case 2:
            return "player DC > 5min, abandon"
        case 3:
            return "player dc, clicked leave, abandon"
        case 4:
            return "player AFK, abandon"
        case 5:
            return "never connected, no abandon"
        case 6:
            return "too long to connect, no abandon"
        case _:
            return "Unknown status"
