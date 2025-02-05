from fastapi import APIRouter, HTTPException
from app.helper.game_mode import get_game_mode
from app.helper.lobby_type import get_lobby_status_description
from app.helper.barrack_status import parse_barracks_status
from app.helper.format_teamfight_participation import format_teamfight_participation
from jsonquery import find_hero_by_id, find_item_by_id_jq
from app.helper.leaver_status import get_leaver_status_description
from app.helper.kill_per_min import kills_per_min_text
from app.helper.format_kda import format_kda
from app.helper.format_lane_efficiency import format_lane_efficiency
import httpx
import json
import os
router = APIRouter(prefix="/matches", tags=["matches"])

@router.get("/{match_id}")
async def get_match(match_id: str):

    file_path = f"matches/{match_id}.json"

    if os.path.exists(file_path):
        print(f"File {file_path} found")
        with open(file_path, "r") as f:
            return json.load(f)
    print(f"File {file_path} not found")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.opendota.com/api/matches/{match_id}")
            response.raise_for_status()

            os.makedirs("matches", exist_ok=True)

            with open(file_path, "w") as f:
                json.dump(response.json(), f, indent=2)

            print(f"File {file_path} saved")
            return response.json()

    except httpx.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

@router.get("/parse/{match_id}")
async def parse_match(match_id: str):
    data = await get_match(match_id)

    players = data['players']
    parsed_players = []
    for player in players:
        hero_found = find_hero_by_id(player["hero_id"])
        if hero_found is None:
            hero_found = "Unknown"

        parsed_player = {
            "account_id": player["account_id"],
            "player_name": player["personaname"],
            "player_slot": "Slot ke " + str(player["player_slot"] + 1),
            "creeps_stacked": player["creeps_stacked"],
            "camps_stacked": player["camps_stacked"],
            "rune_pickups": player["rune_pickups"],
            "firstblood_claimed": player["firstblood_claimed"],
            "teamfight_participation": format_teamfight_participation(player["teamfight_participation"]),
            "towers_killed": player["towers_killed"],
            "roshans_killed": player["roshans_killed"],
            "observers_placed": player["observers_placed"],
            "stuns": str(player["stuns"]) + " kali",
            "account_id": player["account_id"],
            "hero": hero_found[0][0]['localized_name'],
            "slot_item_0": find_item_by_id_jq(player["item_0"]),
            "slot_item_1": find_item_by_id_jq(player["item_1"]),
            "slot_item_2": find_item_by_id_jq(player["item_2"]),
            "slot_item_3": find_item_by_id_jq(player["item_3"]),
            "slot_item_4": find_item_by_id_jq(player["item_4"]),
            "slot_item_5": find_item_by_id_jq(player["item_5"]),
            "item_neutral": find_item_by_id_jq(player["item_neutral"]),
            "backpack_0": find_item_by_id_jq(player["backpack_0"]),
            "backpack_1": find_item_by_id_jq(player["backpack_1"]),
            "backpack_2": find_item_by_id_jq(player["backpack_2"]),
            "kills": str(player["kills"]) + " kali",
            "deaths": str(player["deaths"]) + " kali",
            "assists": str(player["assists"]) + " kali",
            "denies": str(player["denies"]) + " kali",
            "last_hits": str(player["last_hits"]) + " kali",
            "leaver_status": get_leaver_status_description(player["leaver_status"]),
            "gold_per_min": player["gold_per_min"],
            "xp_per_min": player["xp_per_min"],
            "level": player["level"],
            "net_worth": player["net_worth"],
            "aghanims_scepter": "Yes" if player["aghanims_scepter"] == 1 else "No",
            "aghanims_shard": "Yes" if player["aghanims_shard"] == 1 else "No",
            "moonshard": "Yes" if player["moonshard"] == 1 else "No",
            "hero_damage": player["hero_damage"],
            "tower_damage": player["tower_damage"],
            "hero_healing": player["hero_healing"],
            "gold": player["gold"],
            "gold_spent": player["gold_spent"],
            "win": "Yes" if player["radiant_win"] == 1 else "No",
            "lose": "Yes" if player["radiant_win"] == 0 else "No",
            "total_gold": player["total_gold"],
            "total_xp": player["total_xp"],
            "kda": format_kda(player["kda"]),
            "abandons": player["abandons"],
            "neutral_kills": player["neutral_kills"],
            "tower_kills": player["tower_kills"],
            "courier_kills": player["courier_kills"],
            "lane_kills": player["lane_kills"],
            "hero_kills": player["hero_kills"],
            "observer_kills": player["observer_kills"],
            "sentry_kills": player["sentry_kills"],
            "roshan_kills": player["roshans_killed"],
            "ancient_kills": player["ancient_kills"],
            "buyback_count": player["buyback_count"],
            "observer_uses": player["observer_uses"],
            "sentry_uses": player["sentry_uses"],
            "lane_efficiency": format_lane_efficiency(player["lane_efficiency"]) + " atau " + str(player["lane_efficiency_pct"]) + "%",
            "lane": player["lane"],
            "lane_role": player["lane_role"],
            "is_roaming": "Yes" if player["is_roaming"] == 1 else "No",
            "game_mode": await get_game_mode(data['game_mode']),
            "duration": data['duration']
        }
        parsed_players.append(parsed_player)

    parsed_data = {
        "players": parsed_players,
        "radiant_score": data['radiant_score'],
        "dire_score": data['dire_score'],
        "winner": 'radiant' if data['radiant_win'] else 'dire',
        "lobby_status": get_lobby_status_description(data['lobby_type']),
        "barracks_status_radiant": parse_barracks_status(data['barracks_status_radiant']),
        "barracks_status_dire": parse_barracks_status(data['barracks_status_dire'])
    }

    def dict_to_text(d, level=0):
         text = ""
         for key, value in d.items():
             if isinstance(value, dict):
                 text += "  " * level + f"{key}:\n" + dict_to_text(value, level + 1)
             elif isinstance(value, list):
                 text += "  " * level + f"{key}:\n"
                 for item in value:
                     if isinstance(item, dict):
                         text += dict_to_text(item, level + 1)
                     else:
                         text += "  " * (level + 1) + f"- {item}\n"
             else:
                 text += "  " * level + f"{key}: {value}\n"
         return text

    return dict_to_text(parsed_data)