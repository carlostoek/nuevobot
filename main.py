from aiogram import Bot, Dispatcher
from aiogram.utils import executor

from config import get_settings
from database import init_db
from middlewares.auth_middleware import AuthMiddleware
from middlewares.session_middleware import SessionMiddleware
from handlers import start_router, channel_router, gamification_router, missions_router, gifts_router
settings = get_settings()

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(bot)

dp.middleware.setup(AuthMiddleware())
dp.middleware.setup(SessionMiddleware())

dp.include_router(start_router)
dp.include_router(gamification_router)
dp.include_router(missions_router)
dp.include_router(gifts_router)
dp.include_router(channel_router)

if __name__ == '__main__':
    init_db()
    executor.start_polling(dp, skip_updates=True)
