from app.models.history_match import HistoryMatch
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID 
from fastapi import Depends


async def store_history_match(user_id: UUID, match_id: str, db: AsyncSession):
    history_match = HistoryMatch(
        user_id=user_id,
        match_id=match_id
    )
    db.add(history_match)
    await db.commit()
    return history_match.to_dict()