from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Dict, Any

class SessionMiddleware(BaseMiddleware):
    async def on_pre_process_update(self, update: TelegramObject, data: Dict[str, Any]):
        user_ctx = data.get('user_context')
        if user_ctx:
            data['session'] = user_ctx.session_data
