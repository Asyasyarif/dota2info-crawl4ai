from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from dotenv import load_dotenv
import os
import json
from jose import jwt
from app.config.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


async def create_access_token(user_data: dict, expire: datetime):
    to_encode = {
        "sub": json.dumps({
            "id": user_data["id"],
            "username": user_data["username"],
        }),
        "exp": expire,
        "token_type": "access-token"
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_refresh_token(user_data: dict, expire: datetime):
    to_encode = {
        "sub": json.dumps({
            "id": user_data["id"],
            "username": user_data["username"],
        }),
        "exp": expire,
        "token_type": "refresh-token"
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
