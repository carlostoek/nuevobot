from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from database import get_db

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        if event.from_user:
            async with await get_db() as db:
                await db.execute(
                    "INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)",
                    (event.from_user.id, event.from_user.username),
                )
                await db.commit()
        return await handler(event, data)
