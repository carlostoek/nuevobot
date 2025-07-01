"""
Servicio de gestión de usuarios - Fase 2
Implementa CRUD completo y operaciones de perfil
"""
import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

class UserService:
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtiene conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_user(self, telegram_id: int, username: str = None, 
                   first_name: str = None) -> Dict[str, Any]:
        """Crea un nuevo usuario en el sistema"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar si ya existe
                existing = self.get_user(telegram_id)
                if existing:
                    logger.info(f"Usuario {telegram_id} ya existe")
                    return existing
                
                # Crear nuevo usuario
                cursor.execute("""
                    INSERT INTO users (telegram_id, username, first_name, 
                                     besitos, level, is_vip, is_admin, created_at)
                    VALUES (?, ?, ?, 100, 1, 0, 0, ?)
                """, (telegram_id, username, first_name, datetime.now()))
                
                conn.commit()
                logger.success(f"Usuario {telegram_id} creado exitosamente")
                return self.get_user(telegram_id)
                
        except sqlite3.Error as e:
            logger.error(f"Error creando usuario {telegram_id}: {e}")
            return None
    
    def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su telegram_id"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo usuario {telegram_id}: {e}")
            return None
    
    def update_user_besitos(self, telegram_id: int, amount: int) -> bool:
        """Actualiza los besitos de un usuario"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET besitos = besitos + ?, updated_at = ?
                    WHERE telegram_id = ?
                """, (amount, datetime.now(), telegram_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Besitos actualizados para {telegram_id}: {amount}")
                    return True
                return False
                
        except sqlite3.Error as e:
            logger.error(f"Error actualizando besitos {telegram_id}: {e}")
            return False
    
    def set_user_vip(self, telegram_id: int, is_vip: bool) -> bool:
        """Establece el estado VIP de un usuario"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET is_vip = ?, updated_at = ?
                    WHERE telegram_id = ?
                """, (int(is_vip), datetime.now(), telegram_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Estado VIP actualizado para {telegram_id}: {is_vip}")
                    return True
                return False
                
        except sqlite3.Error as e:
            logger.error(f"Error actualizando VIP {telegram_id}: {e}")
            return False
    
    def get_user_channels(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Obtiene los canales suscritos por un usuario"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.* FROM channels c
                    JOIN user_channels uc ON c.id = uc.channel_id
                    WHERE uc.user_id = (SELECT id FROM users WHERE telegram_id = ?)
                    AND uc.is_active = 1
                """, (telegram_id,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo canales usuario {telegram_id}: {e}")
            return []