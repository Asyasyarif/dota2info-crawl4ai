from pysteamsignin.steamsignin import SteamSignIn
from fastapi import FastAPI, Request, Depends
from app.utils.jwt import create_access_token
from datetime import datetime, timedelta
import ssl
import requests
from app.config.settings import settings
from app.models.user import Users
import json
from app.controllers.users_controller import create_or_update_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db_dependency
from app.utils.jwt import create_refresh_token
steam_sign_in = SteamSignIn()
ssl._create_default_https_context = ssl._create_unverified_context

async def steam_login(redirect: bool = True):
    return_url = settings.STEAM_REDIRECT_URL
    login_url = steam_sign_in.ConstructURL(return_url)
    if not redirect:
        return f"https://steamcommunity.com/openid/login?{login_url}"
    return steam_sign_in.RedirectUser(login_url)

async def steam_callback(request: Request, db: AsyncSession = Depends(get_db_dependency)):
    print(request.query_params)
    steam_id = steam_sign_in.ValidateResults(dict(request.query_params))
    if steam_id:
        steam_user = await get_steam_user_data(steam_id)
        print(steam_user)
        user = Users(
            steamid=steam_id,
            name=steam_user.get("personaname", ""),
            email="",
            password="",
            role="user",
            is_activated=True,
            communityvisibilitystate=steam_user.get("communityvisibilitystate", 0),
            profilestate=steam_user.get("profilestate", 0),
            personaname=steam_user.get("personaname", ""),
            commentpermission=steam_user.get("commentpermission", 0),
            profileurl=steam_user.get("profileurl", ""),
            avatar=steam_user.get("avatar", ""),
            avatarmedium=steam_user.get("avatarmedium", ""),
            avatarfull=steam_user.get("avatarfull", ""),
            avatarhash=steam_user.get("avatarhash", ""),
            lastlogoff=steam_user.get("lastlogoff", 0),
            personastate=steam_user.get("personastate", 0),
            realname=steam_user.get("realname", ""),
            primaryclanid=steam_user.get("primaryclanid", ""),
            timecreated=steam_user.get("timecreated", 0),
            personastateflags=steam_user.get("personastateflags", 0),
            loccountrycode=steam_user.get("loccountrycode", ""),
            locstatecode=steam_user.get("locstatecode", ""),
            loccityid=steam_user.get("loccityid", 0)
        )

        result = await create_or_update_user(user)
        if result:
            user_data = {
                "id": result.get("id"),
                "username": result.get("name")
            }

            expired = datetime.now() + timedelta(days=1)
            token = await create_access_token(user_data, expired)
            refresh_token = await create_refresh_token(user_data, expired)
            return {"access_token": token, "refresh_token": refresh_token, "user": user_data}
        else:
            return {"error": "Login gagal"}

    return {"error": "Login gagal"}

async def get_steam_user_data(steam_id: str) -> dict:
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={settings.STEAM_API_KEY}&steamids={steam_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=4))
        return data["response"]["players"][0]
    return {}