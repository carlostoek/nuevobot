from aiogram import Router, types, F
from services.token_service import TokenService
from keyboards import vip_keyboard
from utils.messages import vip_token_message
from middlewares.session_middleware import SessionMiddleware

router = Router()
router.message.middleware(SessionMiddleware())

@router.message(F.text == "👑 Obtener Token VIP")
async def get_vip_token(message: types.Message):
    token = await TokenService.generate_vip_token(user_id=message.from_user.id)
    await message.answer(vip_token_message(token.expiry_date), reply_markup=vip_keyboard())