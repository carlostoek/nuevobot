import aiosqlite
from typing import Optional, Dict, Any, List
from loguru import logger
from config.settings import settings
from database.models import User, Channel, UserChannel
from datetime import datetime

class DatabaseManager:
    """Gestor de conexiones y operaciones de base de datos"""
    
    def __init__(self):
        self.db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        
    async def init_database(self):
        """Inicializa las tablas de la base de datos"""
        async with aiosqlite.connect(self.db_path) as db:
            # Tabla de usuarios
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    besitos INTEGER DEFAULT 100,
                    nivel INTEGER DEFAULT 1,
                    experiencia INTEGER DEFAULT 0,
                    last_daily_reward TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Tabla de canales
            await db.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id INTEGER PRIMARY KEY,
                    channel_name TEXT NOT NULL,
                    channel_username TEXT,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT
                )
            """)
            
            # Tabla de relación usuarios-canales
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_channels (
                    user_telegram_id INTEGER,
                    channel_id INTEGER,
                    joined_at TEXT,
                    is_member BOOLEAN DEFAULT 1,
                    PRIMARY KEY (user_telegram_id, channel_id),
                    FOREIGN KEY (user_telegram_id) REFERENCES users (telegram_id),
                    FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
                )
            """)
            
            await db.commit()
            logger.info("🗄️ Base de datos inicializada correctamente")

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()