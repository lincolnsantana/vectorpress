from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from telegram import Update

from app.core.security import require_telegram_secret
from app.telegram.bot import get_application

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook", dependencies=[Depends(require_telegram_secret)])
async def telegram_webhook(payload: dict) -> JSONResponse:
    application = await get_application()
    if application is None:
        return JSONResponse(
            content={"ok": False, "detail": "Bot não configurado"},
            status_code=503,
        )
    update = Update.de_json(payload, application.bot)
    await application.process_update(update)
    return JSONResponse(content={"ok": True}, status_code=200)
