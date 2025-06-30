from aiogram import types, Router
from middlewares import UserContext
from services.mission_service import MissionService
from utils.keyboards import MAIN_MENU

router = Router()
service = MissionService()

@router.message(lambda m: m.text == '🎯 Misiones')
async def missions(message: types.Message, user_context: UserContext):
    missions = await service.get_user_missions(user_context.user_id)
    if not missions:
        await service.assign_daily_mission(user_context.user_id)
        missions = await service.get_user_missions(user_context.user_id)
    text = '\n'.join(f"- {m.mission.name}: {'✅' if m.completed else '❌'}" for m in missions)
    await message.answer(f"Tus misiones:\n{text}", reply_markup=MAIN_MENU)
