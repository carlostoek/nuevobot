from aiogram.dispatcher.middlewares.base import BaseMiddleware
from database.database import async_session
from database.models import User
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any

class SessionMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Any], event: TelegramObject, data: Dict[str, Any]):
        user_id = event.from_user.id
        async with async_session() as session:
            user = await session.get(User, user_id)
            data['session'] = {'user': user, 'active_auction': None, 'vip_menu_context': ''}
            return await handler(event, data)