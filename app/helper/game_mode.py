async def get_game_mode(game_mode_id: int) -> str:
    match game_mode_id:
        case 0:
            return "Unknown"
        case 1:
            return "All Pick"
        case 2:
            return "Captain's Mode"
        case 3:
            return "Random Draft"
        case 4:
            return "Single Draft"
        case 5:
            return "All Random"
        case 6:
            return "Intro"
        case 7:
            return "Diretide"
        case 8:
            return "Reverse Captain's Mode"
        case 9:
            return "The Greeviling"
        case 10:
            return "Tutorial"
        case 11:
            return "Mid Only"
        case 12:
            return "Least Played"
        case 13:
            return "New Player Pool"
        case 14:
            return "Compendium Matchmaking"
        case 15:
            return "Custom"
        case 16:
            return "Captains Draft"
        case 17:
            return "Balanced Draft"
        case 18:
            return "Ability Draft"
        case 19:
            return "Event (?)"
        case 20:
            return "All Random Death Match"
        case 21:
            return "Solo Mid 1 vs 1"
        case 22:
            return "Ranked All Pick"
        case _:
            return "Unknown"



    