from app.database.database import get_db_dependency
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from app.models.user import Users
from datetime import datetime
from typing import Optional


async def get_all_users(db: AsyncSession = Depends(get_db_dependency)):

    try:
        return (await db.execute(select(Users))).scalars().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def create_or_update_user(user: Users):
    async for db in get_db_dependency():
        try:
            result = await db.execute(select(Users).where(Users.steamid == user.steamid))
            existing_user = result.scalar_one_or_none()
            if existing_user:
                existing_user.name = user.name
                existing_user.email = user.email
                existing_user.password = user.password
                existing_user.role = user.role
                existing_user.is_activated = user.is_activated
                existing_user.updated_at = datetime.now()
                existing_user.communityvisibilitystate = user.communityvisibilitystate
                existing_user.profilestate = user.profilestate
                existing_user.personaname = user.personaname
                existing_user.commentpermission = user.commentpermission
                existing_user.profileurl = user.profileurl
                existing_user.avatar = user.avatar
                existing_user.avatarmedium = user.avatarmedium
                existing_user.avatarfull = user.avatarfull
                existing_user.avatarhash = user.avatarhash
                existing_user.lastlogoff = user.lastlogoff
                existing_user.personastate = user.personastate
                existing_user.realname = user.realname
                existing_user.primaryclanid = user.primaryclanid
                existing_user.timecreated = user.timecreated
                existing_user.personastateflags = user.personastateflags
                existing_user.loccountrycode = user.loccountrycode
                existing_user.locstatecode = user.locstatecode
                existing_user.loccityid = user.loccityid
                await db.commit()
                await db.refresh(existing_user)
                return existing_user.to_dict()
            db.add(user)
            user.created_at = datetime.now()
            await db.commit()
            await db.refresh(user)
            return user.to_dict()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
