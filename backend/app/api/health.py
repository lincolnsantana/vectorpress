from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.database.connection import check_database

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> JSONResponse:
    try:
        payload = await check_database()
        payload["status"] = "ok"
        return JSONResponse(content=payload, status_code=status.HTTP_200_OK)
    except Exception:
        return JSONResponse(
            content={"status": "error", "database": "unavailable", "pgvector": "unknown"},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
