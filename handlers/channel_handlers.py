from aiogram import types, Router
from middlewares import UserContext
from services.channel_service import ChannelService
from utils.keyboards import MAIN_MENU

router = Router()
channel_service = ChannelService()

@router.message(lambda m: m.text == '📺 Canales')
async def list_channels(message: types.Message, user_context: UserContext):
    channels = await channel_service.list_channels()
    if not channels:
        await message.answer('No hay canales disponibles.', reply_markup=MAIN_MENU)
        return
    text = '\n'.join(f"- {c.name}" for c in channels)
    await message.answer(f"Canales disponibles:\n{text}", reply_markup=MAIN_MENU)
