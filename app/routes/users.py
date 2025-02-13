from fastapi import APIRouter, Depends
from app.controllers.users_controller import get_all_users
from app.database.database import get_db_dependency
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Response
from app.utils.response import APIResponse

router = APIRouter(prefix="/users", tags=["users"])
api_response = APIResponse()


@router.get("/")
async def get_users(db: AsyncSession = Depends(get_db_dependency)):
    try:
        users = await get_all_users(db)
        return api_response.success(data=users)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

