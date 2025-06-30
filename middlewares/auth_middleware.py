from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from typing import Any, Callable, Awaitable, Dict

from database import get_db, User
from config import get_settings
from . import UserContext

settings = get_settings()

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            telegram_id = event.from_user.id
            username = event.from_user.username or ""
            first_name = event.from_user.first_name or ""
            with next(get_db()) as db:
                user = db.query(User).filter_by(telegram_id=telegram_id).first()
                if not user:
                    user = User(
                        telegram_id=telegram_id,
                        username=username,
                        first_name=first_name,
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                is_admin = telegram_id in settings.ADMIN_IDS
                context = UserContext(
                    user_id=user.id,
                    telegram_id=telegram_id,
                    username=username,
                    is_admin=is_admin,
                    is_vip=user.vip_status,
                    besitos=user.besitos,
                    level=user.level,
                    session_data={},
                )
                data["user_context"] = context
        return await handler(event, data)
