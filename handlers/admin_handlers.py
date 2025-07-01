from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from services.notification_service import NotificationService
from middlewares.admin_middleware import AdminMiddleware
from keyboards import admin_keyboard, back_keyboard

router = Router()
router.message.middleware(AdminMiddleware())
router.callback_query.middleware(AdminMiddleware())

@router.message(Command("admin"))
async def admin_panel(message: Message, notification_service: NotificationService):
    """Muestra el panel de administración"""
    await message.answer(
        "⚙️ Panel de Administración",
        reply_markup=admin_keyboard()
    )
    await notification_service.send_admin_report(message.from_user.id)

@router.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery, notification_service: NotificationService):
    """Muestra estadísticas actualizadas"""
    await notification_service.send_admin_report(callback.from_user.id)
    await callback.answer()

@router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    """Inicia el proceso de envío masivo"""
    await callback.message.answer(
        "📢 Envía el mensaje que quieres difundir:",
        reply_markup=back_keyboard()
    )
    await state.set_state("admin_broadcast_message")
    await callback.answer()

@router.message(F.text, state="admin_broadcast_message")
async def process_broadcast(message: Message, state: FSMContext, notification_service: NotificationService):
    """Procesa el mensaje para difusión masiva"""
    active_users = await notification_service.db.get_active_users()
    await notification_service.send_batch_notifications(active_users, message.text)
    
    await message.answer(f"📢 Mensaje enviado a {len(active_users)} usuarios!")
    await state.clear()