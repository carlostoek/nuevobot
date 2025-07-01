from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from services.notification_service import NotificationService

router = Router()

@router.message(Command("notify_me"))
async def notify_me_test(message: Message, notification_service: NotificationService):
    """Prueba de notificación personalizada"""
    await notification_service.notify_event(
        message.from_user,
        'welcome',
        level=1
    )

@router.callback_query(F.data.startswith("event_"))
async def handle_user_event(callback: CallbackQuery, notification_service: NotificationService):
    """Maneja eventos de usuario que requieren notificación"""
    event_type = callback.data.split("_")[1]
    
    if event_type == "level_up":
        new_level = int(callback.data.split("_")[2])
        await notification_service.notify_event(
            callback.from_user,
            'level_up',
            level=new_level
        )
    
    await callback.answer()