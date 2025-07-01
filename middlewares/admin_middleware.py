from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from loguru import logger
from datetime import datetime

class AdminMiddleware(BaseMiddleware):
    def __init__(self):
        self.admin_ids = [123456789]  # Reemplazar con IDs reales

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user = event.from_user
        
        if user.id not in self.admin_ids:
            logger.warning(f"Intento de acceso no autorizado de {user.full_name} (ID: {user.id})")
            
            if isinstance(event, Message):
                await event.answer("🔒 Acceso restringido - No tienes permisos de administrador")
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Acción no permitida", show_alert=True)
            
            return
        
        # Log de actividad administrativa
        action = "comando" if isinstance(event, Message) else "callback"
        logger.info(f"Admin {user.full_name} ejecutó {action}: {event.text or event.data}")
        
        return await handler(event, data)