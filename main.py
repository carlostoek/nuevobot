import asyncio
from aiogram import Bot, Dispatcher

from config import get_settings
from database import init_db
from middlewares.auth_middleware import AuthMiddleware
from middlewares.session_middleware import SessionMiddleware
from handlers import (
    start_router,
    channel_router,
    gamification_router,
    missions_router,
    gifts_router,
)
settings = get_settings()

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

# Middlewares (en Aiogram 3.x se agregan así)
dp.update.middleware(AuthMiddleware())
dp.update.middleware(SessionMiddleware())

# Routers
dp.include_router(start_router)
dp.include_router(gamification_router)
dp.include_router(missions_router)
dp.include_router(gifts_router)
dp.include_router(channel_router)

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
