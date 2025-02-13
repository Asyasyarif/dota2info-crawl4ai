from jsonquery import find_hero_by_id, find_item_by_id_jq
from app.controllers.history_controller import store_history_match
from app.helper.leaver_status import get_leaver_status_description
from app.helper.lobby_type import get_lobby_status_description
from app.helper.barrack_status import parse_barracks_status
from app.helper.format_kda import format_kda
from app.helper.game_mode import get_game_mode
from app.helper.format_lane_efficiency import format_lane_efficiency
from app.helper.format_teamfight_participation import format_teamfight_participation
from uuid import UUID
from fastapi import Depends
from app.database.database import get_db_dependency
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import json
import os
from fastapi import HTTPException
from app.models.history_match import HistoryMatch
from sqlalchemy import select

async def get_match_opendota(match_id: str):

    file_path = f"matches/{match_id}.json"
    if os.path.exists(file_path):
        print(f"File {file_path} found")
        with open(file_path, "r") as f:
            return json.load(f)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.opendota.com/api/matches/{match_id}")
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            response.raise_for_status()

            os.makedirs("matches", exist_ok=True)

            with open(file_path, "w") as f:
                json.dump(response.json(), f, indent=2)

            print(f"File {file_path} saved")
            return response.json()

    except httpx.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

async def get_history_match_by_user_id(user_id: UUID, db: AsyncSession):
    history_match = await db.execute(select(HistoryMatch).where(HistoryMatch.user_id == user_id))
    history_match_list = history_match.scalars().all()
    return [
        {
            "id": str(match.id),
            "match_id": match.match_id,
            "created_at": match.created_at.isoformat() if match.created_at else None,
            "updated_at": match.updated_at.isoformat() if match.updated_at else None
        }
        for match in history_match_list
    ]

async def get_match_by_id(match_id: str, user_id: UUID, db: AsyncSession):
    data = await get_match_opendota(match_id)
    if not data:
        raise HTTPException(status_code=404, detail="Match not found")

    # players = data['players']
    # parsed_players = []
    # for player in players:
    #     hero_found = find_hero_by_id(player.get("hero_id"))
    #     if hero_found is None:
    #         hero_found = "-"
        
    #     slot_val = player.get("player_slot")
    #     parsed_player = {
    #         "account_id": player.get("account_id", "-"),
    #         "player_name": player.get("personaname", "-"),
    #         "player_slot": "Slot ke " + (str(slot_val + 1) if slot_val is not None else "-"),
    #         "creeps_stacked": player.get("creeps_stacked", "-"),
    #         "camps_stacked": player.get("camps_stacked", "-"),
    #         "rune_pickups": player.get("rune_pickups", "-"),
    #         "firstblood_claimed": player.get("firstblood_claimed", "-"),
    #         "teamfight_participation": format_teamfight_participation(player.get("teamfight_participation", "-")),
    #         "towers_killed": player.get("towers_killed", "-"),
    #         "roshans_killed": player.get("roshans_killed", "-"),
    #         "observers_placed": player.get("observers_placed", "-"),
    #         "stuns": (str(player["stuns"]) + " kali") if "stuns" in player else "-",
    #         "hero": hero_found[0][0]['localized_name'] if hero_found != "-" else "-",
    #         "slot_item_0": find_item_by_id_jq(player.get("item_0")) if player.get("item_0") is not None else "-",
    #         "slot_item_1": find_item_by_id_jq(player.get("item_1")) if player.get("item_1") is not None else "-",
    #         "slot_item_2": find_item_by_id_jq(player.get("item_2")) if player.get("item_2") is not None else "-",
    #         "slot_item_3": find_item_by_id_jq(player.get("item_3")) if player.get("item_3") is not None else "-",
    #         "slot_item_4": find_item_by_id_jq(player.get("item_4")) if player.get("item_4") is not None else "-",
    #         "slot_item_5": find_item_by_id_jq(player.get("item_5")) if player.get("item_5") is not None else "-",
    #         "item_neutral": find_item_by_id_jq(player.get("item_neutral")) if player.get("item_neutral") is not None else "-",
    #         "backpack_0": find_item_by_id_jq(player.get("backpack_0")) if player.get("backpack_0") is not None else "-",
    #         "backpack_1": find_item_by_id_jq(player.get("backpack_1")) if player.get("backpack_1") is not None else "-",
    #         "backpack_2": find_item_by_id_jq(player.get("backpack_2")) if player.get("backpack_2") is not None else "-",
    #         "kills": (str(player["kills"]) + " kali") if "kills" in player else "-",
    #         "deaths": (str(player["deaths"]) + " kali") if "deaths" in player else "-",
    #         "assists": (str(player["assists"]) + " kali") if "assists" in player else "-",
    #         "denies": (str(player["denies"]) + " kali") if "denies" in player else "-",
    #         "last_hits": (str(player["last_hits"]) + " kali") if "last_hits" in player else "-",
    #         "leaver_status": get_leaver_status_description(player.get("leaver_status")),
    #         "gold_per_min": player.get("gold_per_min", "-"),
    #         "xp_per_min": player.get("xp_per_min", "-"),
    #         "level": player.get("level", "-"),
    #         "net_worth": player.get("net_worth", "-"),
    #         "aghanims_scepter": "Yes" if player.get("aghanims_scepter", 0) == 1 else "No",
    #         "aghanims_shard": "Yes" if player.get("aghanims_shard", 0) == 1 else "No",
    #         "moonshard": "Yes" if player.get("moonshard", 0) == 1 else "No",
    #         "hero_damage": player.get("hero_damage", "-"),
    #         "tower_damage": player.get("tower_damage", "-"),
    #         "hero_healing": player.get("hero_healing", "-"),
    #         "gold": player.get("gold", "-"),
    #         "gold_spent": player.get("gold_spent", "-"),
    #         "win": "Yes" if player.get("radiant_win", 0) == 1 else "No",
    #         "lose": "Yes" if player.get("radiant_win", 0) == 0 else "No",
    #         "total_gold": player.get("total_gold", "-"),
    #         "total_xp": player.get("total_xp", "-"),
    #         "kda": format_kda(player.get("kda", "-")),
    #         "abandons": player.get("abandons", "-"),
    #         "neutral_kills": player.get("neutral_kills", "-"),
    #         "tower_kills": player.get("tower_kills", "-"),
    #         "courier_kills": player.get("courier_kills", "-"),
    #         "lane_kills": player.get("lane_kills", "-"),
    #         "hero_kills": player.get("hero_kills", "-"),
    #         "observer_kills": player.get("observer_kills", "-"),
    #         "sentry_kills": player.get("sentry_kills", "-"),
    #         "roshan_kills": player.get("roshans_killed", "-"),
    #         "ancient_kills": player.get("ancient_kills", "-"),
    #         "buyback_count": player.get("buyback_count", "-"),
    #         "observer_uses": player.get("observer_uses", "-"),
    #         "sentry_uses": player.get("sentry_uses", "-"),
    #         "lane_efficiency": (format_lane_efficiency(player.get("lane_efficiency")) if player.get("lane_efficiency") is not None else "-") + " atau " + (str(player.get("lane_efficiency_pct")) if player.get("lane_efficiency_pct") is not None else "-") + "%",
    #         "lane": player.get("lane", "-"),
    #         "lane_role": player.get("lane_role", "-"),
    #         "is_roaming": "Yes" if player.get("is_roaming", 0) == 1 else "No",
    #         "game_mode": await get_game_mode(data.get('game_mode', "-")),
    #         "duration": data.get('duration', "-")
    #     }
    #     parsed_players.append(parsed_player)

    # parsed_data = {
    #     "players": parsed_players,
    #     "radiant_score": data['radiant_score'],
    #     "dire_score": data['dire_score'],
    #     "winner": 'radiant' if data['radiant_win'] else 'dire',
    #     "lobby_status": get_lobby_status_description(data['lobby_type']),
    #     "barracks_status_radiant": parse_barracks_status(data['barracks_status_radiant']),
    #     "barracks_status_dire": parse_barracks_status(data['barracks_status_dire'])
    # }

    # def dict_to_text(d, level=0):
    #      text = ""
    #      for key, value in d.items():
    #          if isinstance(value, dict):
    #              text += "  " * level + f"{key}:\n" + dict_to_text(value, level + 1)
    #          elif isinstance(value, list):
    #              text += "  " * level + f"{key}:\n"
    #              for item in value:
    #                  if isinstance(item, dict):
    #                      text += dict_to_text(item, level + 1)
    #                  else:
    #                      text += "  " * (level + 1) + f"- {item}\n"
    #          else:
    #              text += "  " * level + f"{key}: {value}\n"
    #      return text

    await store_history_match(user_id, match_id, db)
    return data