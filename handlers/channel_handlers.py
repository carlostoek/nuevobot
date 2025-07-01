"""
Handlers de canales - Fase 2
Maneja la gestión y membresía de canales
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from loguru import logger

from services.user_service import UserService
from services.channel_service import ChannelService
from utils.keyboards import KeyboardBuilder
from utils.messages import Messages

router = Router()
user_service = UserService()
channel_service = ChannelService()

@router.callback_query(F.data == "channels_list")
async def callback_channels_list(callback: CallbackQuery):
    """Mostrar lista de canales disponibles"""
    try:
        telegram_id = callback.from_user.id
        
        # Obtener canales disponibles para el usuario
        channels = channel_service.get_available_channels(telegram_id)
        
        if not channels:
            await callback.message.edit_text(
                text="📺 No hay canales disponibles en este momento.",
                reply_markup=KeyboardBuilder.back_to_main()
            )
            await callback.answer()
            return
        
        # Construir mensaje y teclado
        header_text = Messages.channels_list_header(channels)
        keyboard = KeyboardBuilder.channels_menu(channels)
        
        await callback.message.edit_text(
            text=header_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error en callback_channels_list: {e}")
        await callback.answer("❌ Error al cargar canales")

@router.callback_query(F.data.startswith("channel_join_"))
async def callback_channel_join(callback: CallbackQuery):
    """Unirse a un canal específico"""
    try:
        telegram_id = callback.from_user.id
        channel_id = callback.data.replace("channel_join_", "")
        
        # Obtener información del canal
        channel_data = channel_service.get_channel_by_id(channel_id)
        
        if not channel_data:
            await callback.answer(Messages.error_channel_not_found())
            return
        
        # Verificar si es canal VIP y el usuario no es VIP
        if channel_data['is_vip']:
            user_data = user_service.get_user(telegram_id)
            if not user_data or not user_data.get('is_vip'):
                await callback.answer(Messages.error_vip_required())
                return
        
        # Intentar unir al usuario
        success = channel_service.join_user_to_channel(telegram_id, channel_id)
        
        if success:
            # Dar recompensa en besitos
            reward = channel_data.get('reward_besitos', 50)
            user_service.update_user_besitos(telegram_id, reward)
            
            success_message = Messages.success_channel_joined(
                channel_data['name'], reward
            )
            
            await callback.answer(success_message, show_alert=True)
            
            # Actualizar la vista de canales
            channels = channel_service.get_available_channels(telegram_id)
            header_text = Messages.channels_list_header(channels)
            keyboard = KeyboardBuilder.channels_menu(channels)
            
            await callback.message.edit_text(
                text=header_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            await callback.answer("❌ Error al unirse al canal")
        
    except Exception as e:
        logger.error(f"Error en callback_channel_join: {e}")
        await callback.answer("❌ Error interno")

@router.callback_query(F.data == "back_to_main")
async def callback_back_to_main(callback: CallbackQuery):
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
        logger.error(f"Error en callback_back_to_main: {e}")
        await callback.answer("❌ Error interno")