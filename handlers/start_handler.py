"""
Handler principal /start - Fase 2
Maneja el comando inicial y navegación básica
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from loguru import logger

from services.user_service import UserService
from utils.keyboards import KeyboardBuilder
from utils.messages import Messages

router = Router()
user_service = UserService()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Maneja el comando /start"""
    try:
        telegram_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        
        # Obtener o crear usuario
        user_data = user_service.get_user(telegram_id)
        
        if user_data:
            # Usuario existente
            welcome_text = Messages.welcome_message(user_data)
            logger.info(f"Usuario existente {telegram_id} accedió")
        else:
            # Crear nuevo usuario
            user_data = user_service.create_user(telegram_id, username, first_name)
            if user_data:
                welcome_text = Messages.new_user_welcome(user_data)
                logger.success(f"Nuevo usuario {telegram_id} creado")
            else:
                await message.answer("❌ Error al crear usuario. Intenta de nuevo.")
                return
        
        # Enviar mensaje de bienvenida con teclado
        keyboard = KeyboardBuilder.main_menu(user_data)
        
        await message.answer(
            text=welcome_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en cmd_start: {e}")
        await message.answer("❌ Error interno. Contacta al administrador.")

@router.callback_query(F.data == "main_home")
async def callback_main_home(callback: CallbackQuery):
    """Volver al menú principal"""
    try:
        telegram_id = callback.from_user.id
        user_data = user_service.get_user(telegram_id)
        
        if not user_data:
            await callback.answer("❌ Usuario no encontrado")
            return
        
        welcome_text = Messages.welcome_message(user_data)
        keyboard = KeyboardBuilder.main_menu(user_data)
        
        await callback.message.edit_text(
            text=welcome_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error en callback_main_home: {e}")
        await callback.answer("❌ Error interno")

@router.callback_query(F.data == "profile")
async def callback_profile(callback: CallbackQuery):
    """Mostrar perfil del usuario"""
    try:
        telegram_id = callback.from_user.id
        user_data = user_service.get_user(telegram_id)
        
        if not user_data:
            await callback.answer("❌ Usuario no encontrado")
            return
        
        profile_text = Messages.profile_info(user_data)
        keyboard = KeyboardBuilder.back_to_main()
        
        await callback.message.edit_text(
            text=profile_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error en callback_profile: {e}")
        await callback.answer("❌ Error interno")