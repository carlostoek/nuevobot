from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Any, Callable, Awaitable, Dict

class SessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_ctx = data.get("user_context")
        if user_ctx:
            data["session"] = user_ctx.session_data
        return await handler(event, data)
