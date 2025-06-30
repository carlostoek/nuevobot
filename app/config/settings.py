# config/settings.py
import os
from typing import List

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "TU_TOKEN_AQUI")
DATABASE_URL = "sqlite:///bot_mvp.db"

# Admin Configuration
ADMIN_IDS: List[int] = [
    123456789,  # Reemplaza con tu Telegram ID
]

# Gamification Settings
DAILY_GIFT_BESITOS = 10
WELCOME_BESITOS = 50
LEVEL_MULTIPLIER = 100  # besitos needed per level

# Messages Configuration
WELCOME_MESSAGE = """
🎉 ¡Bienvenido al Bot MVP! 

Has recibido {besitos} besitos de bienvenida.
Usa el menú para navegar por las funciones disponibles.
"""

DAILY_GIFT_MESSAGE = """
🎁 ¡Regalo Diario Reclamado!

Has recibido {besitos} besitos.
¡Vuelve mañana por más recompensas!

💰 Total de besitos: {total_besitos}
"""

# Database Configuration
DATABASE_CONFIG = {
    "echo": False,  # Set to True for SQL debugging
    "check_same_thread": False
}