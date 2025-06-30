import os
from typing import List
from dotenv import load_dotenv
from loguru import logger

# Cargar variables de entorno
load_dotenv()

class Settings:
    """Configuración global del bot"""
    
    # Bot Configuration
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///adventure_bot.db")
    
    # Admin Configuration
    ADMIN_IDS: List[int] = [
        int(admin_id.strip()) 
        for admin_id in os.getenv("ADMIN_IDS", "").split(",") 
        if admin_id.strip().isdigit()
    ]
    
    # Debug Configuration
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Game Configuration
    INITIAL_BESITOS: int = int(os.getenv("INITIAL_BESITOS", "100"))
    DAILY_REWARD: int = int(os.getenv("DAILY_REWARD", "50"))
    
    @classmethod
    def validate_config(cls) -> bool:
        """Valida la configuración del bot"""
        if not cls.BOT_TOKEN:
            logger.error("❌ BOT_TOKEN no está configurado")
            return False
        
        if not cls.DATABASE_URL:
            logger.error("❌ DATABASE_URL no está configurado")
            return False
        
        logger.info("✅ Configuración validada correctamente")
        return True

# Instancia global de configuración
settings = Settings()