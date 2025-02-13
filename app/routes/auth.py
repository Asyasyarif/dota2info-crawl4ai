
from fastapi import APIRouter, HTTPException, Request
from app.controllers.steam_controller import steam_login, steam_callback
from app.utils.response import APIResponse
import logging

response = APIResponse()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/steam/login")
async def steam_login_route(redirect: bool = True):
    try:
        if redirect:
            return await steam_login(redirect=redirect)
        else:
            return response.success(await steam_login(redirect=redirect))
    except Exception as e:
        logger.error(f"Error logging in: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/steam/callback")
async def steam_callback_route(request: Request):
    try:
        res = await steam_callback(request)
        return response.success(res)
    except Exception as e:
        print(e)
        logger.error(f"Error logging in: {e}")
        raise HTTPException(status_code=500, detail=str(e))
