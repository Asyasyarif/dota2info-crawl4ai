import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.settings import settings
from app.routes import matches, chats, users, auth
from app.database.database import get_db_dependency
from sqlalchemy import text
import asyncio
from app.database.init_db import init_db


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches.router, prefix=settings.API_PREFIX)
app.include_router(chats.router, prefix=settings.API_PREFIX)
app.include_router(users.router, prefix=settings.API_PREFIX)
app.include_router(auth.router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    return {"message": "hi"}

@app.get("/health-check")
async def health_check(db: AsyncSession = Depends(get_db_dependency)):
    result = await db.execute(text("SELECT 1"))
    value = result.scalar()
    return {"health": "ok", "check": value}


if __name__ == "__main__":
    asyncio.run(init_db())
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000,
                reload=True, loop="asyncio", log_level="debug")