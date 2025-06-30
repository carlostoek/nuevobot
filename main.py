from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import get_settings
from database import init_db
from middlewares.auth_middleware import AuthMiddleware
from middlewares.session_middleware import SessionMiddleware

settings = get_settings()

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(bot)

dp.middleware.setup(AuthMiddleware())
dp.middleware.setup(SessionMiddleware())

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "\ud83c\udf89 \u00a1Bienvenido, Aventurero!\n\n"
        "\u00a1Has comenzado tu \u00e9pica aventura! Aqu\u00ed podr\u00e1s ganar besitos \ud83d\udc96, completar misiones \ud83c\udfaf y desbloquear contenido exclusivo.\n\n"
        "\u2728 Estado: Nuevo aventurero\n\ud83c\udf81 Regalo inicial: 100 besitos\n\n"
        "\ud83c\udfe0 Usa el men\u00fa para comenzar tu aventura"
    )

if __name__ == '__main__':
    init_db()
    executor.start_polling(dp, skip_updates=True)
