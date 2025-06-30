from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class SessionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        data.setdefault('session', {})
        return await handler(event, data)
