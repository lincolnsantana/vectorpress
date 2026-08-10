from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler

from app.core.config import settings
from app.telegram.commands import ask_handler, list_handler, today_handler

_application: Application | None = None


def build_application() -> Application:
    application = (
        ApplicationBuilder()
        .token(settings.telegram_token)
        .build()
    )
    application.add_handler(CommandHandler("today", today_handler))
    application.add_handler(CommandHandler("list", list_handler))
    application.add_handler(CommandHandler("ask", ask_handler))
    return application


async def get_application() -> Application | None:
    global _application
    if _application is not None:
        return _application
    if not settings.telegram_token:
        return None
    application = build_application()
    await application.initialize()
    _application = application
    return _application


async def shutdown_application() -> None:
    global _application
    if _application is not None:
        await _application.shutdown()
        _application = None
