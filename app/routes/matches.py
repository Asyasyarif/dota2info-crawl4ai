from fastapi import APIRouter, HTTPException
from fastapi import Depends
from uuid import UUID
from app.database.database import get_db_dependency
from sqlalchemy.ext.asyncio import AsyncSession
from app.middleware.auth import get_current_user
from app.controllers.match_controller import get_match_by_id, get_history_match_by_user_id
from app.utils.response import APIResponse

router = APIRouter(prefix="/matches", tags=["matches"])
apiResponse = APIResponse()

@router.get("/parse/{match_id}")
async def parse_match(match_id: str, db: AsyncSession = Depends(get_db_dependency), current_user: dict = Depends(get_current_user)):
    try:
        user_id = UUID(current_user.get("id"))
        response = await get_match_by_id(match_id, user_id, db)
        return apiResponse.success(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_history_match(db: AsyncSession = Depends(get_db_dependency), current_user: dict = Depends(get_current_user)):
    try:
        user_id = UUID(current_user.get("id"))
        response = await get_history_match_by_user_id(user_id, db)
        return apiResponse.success(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
