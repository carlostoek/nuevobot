# middlewares/auth_middleware.py
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from database.models import db
from config.settings import ADMIN_IDS

class AuthMiddleware(BaseMiddleware):
    """Middleware to handle user authentication and data"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user: User = data.get("event_from_user")
        
        if user:
            # Get or create user in database
            user_data = await db.get_user(user.id)
            
            if not user_data:
                # Create new user
                user_data = await db.create_user(
                    telegram_id=user.id,
                    username=user.username or "",
                    first_name=user.first_name or ""
                )
            
            # Add user data to handler context
            data["user_data"] = user_data
            data["is_admin"] = user.id in ADMIN_IDS
        
        return await handler(event, data)