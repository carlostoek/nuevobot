from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math
from database.database import get_db
from models.user import User
from utils.logger import logger

class GamificationService:
    """Servicio para gestionar el sistema de gamificación."""
    
    # Configuración de niveles
    BASE_POINTS_PER_LEVEL = 100
    LEVEL_MULTIPLIER = 1.5
    MAX_LEVEL = 50
    
    # Configuración de puntos
    POINTS_PER_REACTION = 10
    POINTS_PER_MESSAGE = 5
    POINTS_PER_MISSION = 50
    POINTS_PER_ACHIEVEMENT = 100
    
    def __init__(self):
        self.db = get_db()
    
    def calculate_level_requirements(self, level: int) -> int:
        """Calcula los puntos necesarios para alcanzar un nivel."""
        if level <= 1:
            return 0
        
        total_points = 0
        for i in range(1, level):
            points_for_level = int(self.BASE_POINTS_PER_LEVEL * (self.LEVEL_MULTIPLIER ** (i - 1)))
            total_points += points_for_level
        
        return total_points
    
    def calculate_user_level(self, total_points: int) -> Tuple[int, int, int]:
        """
        Calcula el nivel actual del usuario y progreso.
        Returns: (nivel_actual, puntos_para_siguiente, puntos_faltantes)
        """
        level = 1
        while level < self.MAX_LEVEL:
            required_points = self.calculate_level_requirements(level + 1)
            if total_points < required_points:
                break
            level += 1
        
        points_for_next = self.calculate_level_requirements(level + 1) if level < self.MAX_LEVEL else 0
        points_needed = max(0, points_for_next - total_points)
        
        return level, points_for_next, points_needed
    
    async def add_points(self, user_id: int, points: int, reason: str = "") -> Dict:
        """
        Añade puntos a un usuario y verifica subida de nivel.
        Returns: {"level_up": bool, "new_level": int, "total_points": int}
        """
        try:
            cursor = self.db.cursor()
            
            # Obtener puntos actuales
            cursor.execute("SELECT besitos, level FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"Usuario {user_id} no encontrado para añadir {points} puntos")
                return {"level_up": False, "new_level": 1, "total_points": 0}
            
            current_points, current_level = result
            new_total_points = current_points + points
            
            # Calcular nuevo nivel
            new_level, _, _ = self.calculate_user_level(new_total_points)
            level_up = new_level > current_level
            
            # Actualizar base de datos
            cursor.execute("""
                UPDATE users 
                SET besitos = ?, level = ?, updated_at = ?
                WHERE user_id = ?
            """, (new_total_points, new_level, datetime.now(), user_id))
            
            self.db.commit()
            
            if level_up:
                logger.info(f"Usuario {user_id} subió al nivel {new_level} con {new_total_points} besitos")
            
            return {
                "level_up": level_up,
                "new_level": new_level,
                "total_points": new_total_points,
                "points_added": points
            }
            
        except Exception as e:
            logger.error(f"Error añadiendo puntos: {e}")
            return {"level_up": False, "new_level": 1, "total_points": 0}