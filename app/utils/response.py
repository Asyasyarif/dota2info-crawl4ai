from typing import Any, Optional
from fastapi.responses import JSONResponse
from fastapi import status
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class APIResponse:
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "data": data,
                "message": message,
                "success": True,
                "code": code
            }
        )

    @staticmethod
    def created(
        data: Any = None,
        message: str = "Created",
        code: int = status.HTTP_201_CREATED
    ) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "data": data,
                "message": message,
                "success": True,
                "code": code
            }
        )

    @staticmethod
    def error(
        message: str = "Error",
        code: int = status.HTTP_400_BAD_REQUEST,
        data: Optional[Any] = None
    ) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "data": data,
                "message": message,
                "success": False,
                "code": code
            }
        )

    @staticmethod
    def not_found(
        message: str = "Not Found",
        code: int = status.HTTP_404_NOT_FOUND
    ) -> JSONResponse:
        return APIResponse.error(message, code)

    @staticmethod
    def pagination(
        data: list,
        total: int,
        page: int,
        limit: int,
        message: str = "Success",
        code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "data": data,
                "message": message,
                "success": True,
                "code": code,
                "meta": {
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "total_pages": -(-total // limit)  # Ceil division
                }
            }
        )

response = APIResponse()