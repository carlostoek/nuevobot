# handlers/main_handlers.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from utils.keyboards import main_menu_keyboard, profile_keyboard, admin_keyboard, back_to_admin_keyboard
from database.models import db
from config.settings import WELCOME_MESSAGE, DAILY_GIFT_MESSAGE

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message, user_data: dict, is_admin: bool):
    """Handle /start command"""
    await message.answer(
        WELCOME_MESSAGE.format(besitos=user_data['besitos']),
        reply_markup=main_menu_keyboard(is_admin)
    )

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, is_admin: bool):
    """Handle main menu callback"""
    await callback.message.edit_text(
        "🏠 Menú Principal\n\nSelecciona una opción:",
        reply_markup=main_menu_keyboard(is_admin)
    )
    await callback.answer()

@router.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery, user_data: dict):
    """Handle profile callback"""
    level_progress = (user_data['besitos'] % 100) / 100 * 10
    progress_bar = "█" * int(level_progress) + "░" * (10 - int(level_progress))
    
    profile_text = f"""
🏆 **Mi Perfil**

👤 **Usuario:** {user_data.get('first_name', 'Sin nombre')}
💰 **Besitos:** {user_data['besitos']}
⭐ **Nivel:** {user_data['level']}

📊 **Progreso al siguiente nivel:**
{progress_bar} {int(level_progress * 10)}%

🎯 **Necesitas {100 - (user_data['besitos'] % 100)} besitos más para subir de nivel**
"""
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=profile_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "daily_gift")
async def daily_gift_callback(callback: CallbackQuery, user_data: dict, is_admin: bool):
    """Handle daily gift callback"""
    success = await db.claim_daily_gift(user_data['telegram_id'])
    
    if success:
        # Get updated user data
        updated_user = await db.get_user(user_data['telegram_id'])
        
        await callback.message.edit_text(
            DAILY_GIFT_MESSAGE.format(
                besitos=10,  # DAILY_GIFT_BESITOS
                total_besitos=updated_user['besitos']
            ),
            reply_markup=main_menu_keyboard(is_admin)
        )
    else:
        await callback.message.edit_text(
            "⏰ **Regalo Diario**\n\nYa has reclamado tu regalo de hoy.\n¡Vuelve mañana por más besitos! 🎁",
            reply_markup=main_menu_keyboard(is_admin),
            parse_mode="Markdown"
        )
    
    await callback.answer()

@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery, is_admin: bool):
    """Handle help callback"""
    help_text = """
ℹ️ **Ayuda del Bot MVP**

🎁 **Regalo Diario:** Reclama besitos gratis cada día
🏆 **Mi Perfil:** Ve tus estadísticas y progreso
⭐ **Niveles:** Sube de nivel acumulando besitos

💰 **Besitos:** Moneda del bot para recompensas
📊 **Progreso:** 100 besitos = 1 nivel

¡Más funciones próximamente! 🚀
"""
    
    await callback.message.edit_text(
        help_text,
        reply_markup=main_menu_keyboard(is_admin),
        parse_mode="Markdown"
    )
    await callback.answer()