from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import admin_handlers, notifications_handlers
from middlewares import admin_middleware
from services.notification_service import NotificationService

async def main():
    bot = Bot(token="TU_TOKEN")
    dp = Dispatcher(storage=MemoryStorage())
    
    # Configuración de servicios
    notification_service = NotificationService(bot, db)  # db debe ser tu instancia de base de datos
    
    # Registrar middlewares
    admin_handlers.router.message.middleware(admin_middleware.AdminMiddleware())
    
    # Registrar routers
    dp.include_router(admin_handlers.router)
    dp.include_router(notifications_handlers.router)
    
    # Inyectar dependencias
    dp.update.outer_middleware(admin_middleware.AdminMiddleware())
    dp["notification_service"] = notification_service
    
    await dp.start_polling(bot)