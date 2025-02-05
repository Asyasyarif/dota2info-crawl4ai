def get_lobby_status_description(status: int) -> str:
    match status:
        case -1:
            return "Invalid"
        case 0:
            return "Public matchmaking"
        case 1:
            return "Practice"
        case 2:
            return "Tournament"
        case 3:
            return "Tutorial"
        case 4:
            return "Co-op with AI"
        case 5:
            return "Team match"
        case 6:
            return "Solo queue"
        case 7:
            return "Ranked matchmaking"
        case _:
            return "Unknown status"
