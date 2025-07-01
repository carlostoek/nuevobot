"""
Servicio de gestión de canales - Fase 2
Implementa CRUD y validación de membresías
"""
import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

MAX_CHANNELS_PER_USER = 10
CHANNEL_VERIFICATION_TIMEOUT = 300

class ChannelService:
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtiene conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_channel(self, name: str, channel_id: str, 
                      is_vip: bool = False, reward_besitos: int = 50) -> Dict[str, Any]:
        """Crea un nuevo canal en el sistema"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar si ya existe
                existing = self.get_channel_by_id(channel_id)
                if existing:
                    logger.info(f"Canal {channel_id} ya existe")
                    return existing
                
                cursor.execute("""
                    INSERT INTO channels (name, channel_id, is_vip, reward_besitos, 
                                        is_active, created_at)
                    VALUES (?, ?, ?, ?, 1, ?)
                """, (name, channel_id, int(is_vip), reward_besitos, datetime.now()))
                
                conn.commit()
                logger.success(f"Canal {name} creado exitosamente")
                return self.get_channel_by_id(channel_id)
                
        except sqlite3.Error as e:
            logger.error(f"Error creando canal {name}: {e}")
            return None
    
    def get_channel_by_id(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un canal por su ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM channels WHERE channel_id = ?", (channel_id,))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo canal {channel_id}: {e}")
            return None
    
    def get_available_channels(self, user_telegram_id: int) -> List[Dict[str, Any]]:
        """Obtiene canales disponibles para un usuario"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Obtener info del usuario
                cursor.execute("SELECT is_vip FROM users WHERE telegram_id = ?", 
                             (user_telegram_id,))
                user_row = cursor.fetchone()
                
                if not user_row:
                    return []
                
                is_vip = user_row['is_vip']
                
                # Obtener canales disponibles
                if is_vip:
                    cursor.execute("SELECT * FROM channels WHERE is_active = 1")
                else:
                    cursor.execute("SELECT * FROM channels WHERE is_active = 1 AND is_vip = 0")
                
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo canales disponibles: {e}")
            return []
    
    def join_user_to_channel(self, telegram_id: int, channel_id: str) -> bool:
        """Suscribe un usuario a un canal"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Obtener IDs
                cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
                user_row = cursor.fetchone()
                
                cursor.execute("SELECT id FROM channels WHERE channel_id = ?", (channel_id,))
                channel_row = cursor.fetchone()
                
                if not user_row or not channel_row:
                    return False
                
                user_id = user_row['id']
                channel_db_id = channel_row['id']
                
                # Verificar si ya está suscrito
                cursor.execute("""
                    SELECT id FROM user_channels 
                    WHERE user_id = ? AND channel_id = ? AND is_active = 1
                """, (user_id, channel_db_id))
                
                if cursor.fetchone():
                    logger.info(f"Usuario {telegram_id} ya está en canal {channel_id}")
                    return True
                
                # Crear suscripción
                cursor.execute("""
                    INSERT INTO user_channels (user_id, channel_id, joined_at, is_active)
                    VALUES (?, ?, ?, 1)
                """, (user_id, channel_db_id, datetime.now()))
                
                conn.commit()
                logger.success(f"Usuario {telegram_id} unido a canal {channel_id}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error uniendo usuario a canal: {e}")
            return False