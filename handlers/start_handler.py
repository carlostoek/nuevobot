from aiogram import Router, types
from aiogram.filters import CommandStart
from middlewares import UserContext
from utils.keyboards import MAIN_MENU
from utils.messages import WELCOME_MESSAGE

router = Router()

@router.message(CommandStart())
async def start(message: types.Message, user_context: UserContext):
    text = WELCOME_MESSAGE.format(
        besitos=user_context.besitos,
        level=user_context.level,
        channels=len(user_context.session_data.get('channels', [])),
    )
    await message.answer(text, reply_markup=MAIN_MENU)
