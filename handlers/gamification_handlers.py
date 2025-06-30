from aiogram import types, Router
from middlewares import UserContext
from services.gamification_service import GamificationService
from utils.keyboards import MAIN_MENU

router = Router()
service = GamificationService()

@router.message(lambda m: m.text == '🏆 Mi Perfil')
async def profile(message: types.Message, user_context: UserContext):
    text = (
        f"💖 Besitos: {user_context.besitos}\n"
        f"⭐ Nivel: {user_context.level}"
    )
    await message.answer(text, reply_markup=MAIN_MENU)
