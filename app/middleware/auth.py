import os
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db_dependency
from datetime import datetime
from app.config.settings import settings
import json

ENCRYPTION_KEY = settings.ENCRYPTION_KEY.encode()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db_dependency)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("token_type") != "access-token":
            raise credentials_exception

        user_data = payload.get("sub")
        if isinstance(user_data, str):
            import json
            try:
                user_data = json.loads(user_data)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="invalid token format"
                )

        if user_data is None:
            raise credentials_exception

        return user_data
    except JWTError as e:
        print("error middleware", e)
        raise credentials_exception


    try:
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing authorization header"
            )

        api_key = authorization.split(' ')[1]
        data = decode_api_key(api_key)

        if data.get("expires_at"):
            try:
                expired_date = datetime.fromisoformat(
                    data["expires_at"].replace('T', ' '))
                current_time = datetime.now(expired_date.tzinfo)
                if expired_date < current_time:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="API key is expired"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid expiry date format"
                )

        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid API key: {str(e)}"
        )