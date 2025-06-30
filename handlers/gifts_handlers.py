from aiogram import types, Router
from middlewares import UserContext
from services.gift_service import GiftService
from utils.keyboards import MAIN_MENU

router = Router()
service = GiftService()

@router.message(lambda m: m.text == '🎁 Regalo Diario')
async def daily_gift(message: types.Message, user_context: UserContext):
    claimed = await service.claim_daily_gift(user_context.user_id)
    if claimed:
        await message.answer('🎁 Has recibido 20 besitos!', reply_markup=MAIN_MENU)
    else:
        await message.answer('⏳ Ya reclamaste el regalo de hoy.', reply_markup=MAIN_MENU)
