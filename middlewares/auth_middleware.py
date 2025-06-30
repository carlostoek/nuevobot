from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
import aiosqlite
from loguru import logger
from database.connection import db_manager
from database.models import User
from config.settings import settings
from datetime import datetime

class AuthMiddleware(BaseMiddleware):
    """Middleware para autenticación y registro automático de usuarios"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        
        # Obtener información del usuario
        user_data = event.from_user
        
        if not user_data:
            logger.warning("⚠️ Evento sin información de usuario")
            return await handler(event, data)
        
        # Buscar o crear usuario en la base de datos
        user = await self.get_or_create_user(user_data)
        
        # Agregar usuario al contexto de datos
        data["user"] = user
        data["user_context"] = UserContext(user)
        
        return await handler(event, data)
    
    async def get_or_create_user(self, user_data) -> User:
        """Obtiene o crea un usuario en la base de datos"""
        async with aiosqlite.connect(db_manager.db_path) as db:
            # Buscar usuario existente
            cursor = await db.execute(
                "SELECT * FROM users WHERE telegram_id = ?", 
                (user_data.id,)
            )
            row = await cursor.fetchone()
            
            if row:
                # Usuario existe, actualizar información
                user = User(
                    telegram_id=row[0],
                    username=row[1],
                    first_name=row[2],
                    last_name=row[3],
                    besitos=row[4],
                    nivel=row[5],
                    experiencia=row[6],
                    last_daily_reward=datetime.fromisoformat(row[7]) if row[7] else None,
                    created_at=datetime.fromisoformat(row[8]) if row[8] else None,
                    updated_at=datetime.fromisoformat(row[9]) if row[9] else None,
                    is_active=bool(row[10])
                )
                
                # Actualizar datos del usuario
                await db.execute("""
                    UPDATE users SET username = ?, first_name = ?, 
                    last_name = ?, updated_at = ? WHERE telegram_id = ?
                """, (
                    user_data.username,
                    user_data.first_name,
                    user_data.last_name,
                    datetime.now().isoformat(),
                    user_data.id
                ))
                
            else:
                # Crear nuevo usuario
                user = User(
                    telegram_id=user_data.id,
                    username=user_data.username,
                    first_name=user_data.first_name,
                    last_name=user_data.last_name,
                    besitos=settings.INITIAL_BESITOS
                )
                
                await db.execute("""
                    INSERT INTO users (telegram_id, username, first_name, 
                    last_name, besitos, nivel, experiencia, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user.telegram_id,
                    user.username,
                    user.first_name,
                    user.last_name,
                    user.besitos,
                    user.nivel,
                    user.experiencia,
                    user.created_at.isoformat(),
                    user.updated_at.isoformat()
                ))
                
                logger.info(f"👤 Nuevo usuario registrado: {user.telegram_id}")
            
            await db.commit()
            return user

class UserContext:
    """Contexto de usuario para operaciones específicas"""
    
    def __init__(self, user: User):
        self.user = user
    
    def get_display_name(self) -> str:
        """Obtiene el nombre para mostrar del usuario"""
        if self.user.first_name:
            return self.user.first_name
        elif self.user.username:
            return f"@{self.user.username}"
        else:
            return f"Usuario {self.user.telegram_id}"
    
    def can_claim_daily_reward(self) -> bool:
        """Verifica si el usuario puede reclamar el regalo diario"""
        if not self.user.last_daily_reward:
            return True
        
        # Verificar si ha pasado 24 horas
        now = datetime.now()
        time_diff = now - self.user.last_daily_reward
        return time_diff.days >= 1