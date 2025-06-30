"""
Admin handlers - Panel básico de administración
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from middlewares.admin_middleware import AdminMiddleware
from utils.keyboards import AdminKeyboards
from utils.messages import AdminMessages
from services.admin_service import AdminService
from services.user_service import UserService

router = Router()
router.message.middleware(AdminMiddleware())
router.callback_query.middleware(AdminMiddleware())

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Panel principal de administración"""
    keyboard = AdminKeyboards.main_panel()
    stats = await AdminService.get_basic_stats()
    
    text = AdminMessages.admin_panel(stats)
    await message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """Estadísticas detalladas"""
    stats = await AdminService.get_detailed_stats()
    text = AdminMessages.detailed_stats(stats)
    
    keyboard = AdminKeyboards.back_to_admin()
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    """Lista de usuarios"""
    users = await UserService.get_recent_users(10)
    text = AdminMessages.users_list(users)
    
    keyboard = AdminKeyboards.users_panel()
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery):
    """Preparar broadcast"""
    text = AdminMessages.broadcast_instructions()
    keyboard = AdminKeyboards.back_to_admin()
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    """Volver al panel admin"""
    stats = await AdminService.get_basic_stats()
    text = AdminMessages.admin_panel(stats)
    keyboard = AdminKeyboards.main_panel()
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.message(Command("broadcast"))
async def broadcast_message(message: Message):
    """Enviar mensaje masivo"""
    if not message.reply_to_message:
        await message.answer("Responde a un mensaje para hacer broadcast")
        return
    
    result = await AdminService.broadcast_message(
        message.reply_to_message.text or "Mensaje multimedia"
    )
    
    await message.answer(f"Broadcast enviado a {result['sent']} usuarios")