"""
Bot Telegram MVP - Punto de entrada principal
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.settings import get_settings
from database.connection import init_db
from middlewares.auth_middleware import AuthMiddleware
from middlewares.session_middleware import SessionMiddleware

# Importar handlers
from handlers import (
    start_handlers,
    profile_handlers,
    daily_gift_handlers,
    help_handlers,
    admin_handlers
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def setup_bot():
    """Configurar bot y dispatcher"""
    settings = get_settings()
    
    # Crear bot con configuración por defecto
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Crear dispatcher
    dp = Dispatcher()
    
    # Registrar middlewares globales
    dp.message.middleware(SessionMiddleware())
    dp.callback_query.middleware(SessionMiddleware())
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    # Registrar routers
    dp.include_router(start_handlers.router)
    dp.include_router(profile_handlers.router)
    dp.include_router(daily_gift_handlers.router)
    dp.include_router(help_handlers.router)
    dp.include_router(admin_handlers.router)
    
    return bot, dp

async def on_startup():
    """Tareas de inicio"""
    logger.info("Iniciando bot...")
    await init_db()
    logger.info("Base de datos inicializada")

async def on_shutdown(bot: Bot):
    """Tareas de cierre"""
    logger.info("Cerrando bot...")
    await bot.session.close()

async def main():
    """Función principal"""
    try:
        # Configurar bot
        bot, dp = await setup_bot()
        
        # Configurar eventos
        dp.startup.register(on_startup)
        dp.shutdown.register(lambda: on_shutdown(bot))
        
        # Obtener info del bot
        bot_info = await bot.get_me()
        logger.info(f"Bot iniciado: @{bot_info.username}")
        
        # Iniciar polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error crítico: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"Error fatal: {e}")