import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from config import Settings
from database import create_tables
from middlewares import AuthMiddleware, SessionMiddleware

settings = Settings()

bot = Bot(settings.bot_token)
dp = Dispatcher()

dp.message.middleware(AuthMiddleware())
dp.message.middleware(SessionMiddleware())

@dp.message(Command('start'))
async def cmd_start(message: Message):
    text = (
        "\U0001F389 \u00a1Bienvenido, Aventurero!\n\n"
        "\u00a1Has comenzado tu \u00e9pica aventura! Aqu\u00ed podr\u00e1s ganar besitos \u2764\ufe0f\n\n"
        "\u2728 Estado: Nuevo aventurero\n"
        "\ud83c\udf81 Regalo inicial: 100 besitos\n\n"
        "\ud83c\udfe0 Usa el men\u00fa para comenzar tu aventura"
    )
    await message.answer(text)

async def main():
    logger.remove()
    logger.add(lambda msg: print(msg, end=""), level=settings.log_level)
    await create_tables()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
