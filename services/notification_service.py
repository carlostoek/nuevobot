from loguru import logger
from typing import List, Optional
from aiogram.types import User
from datetime import datetime, timedelta
import random

class NotificationService:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.batch_size = 100
        self.humor_messages = {
            'welcome': [
                "¡Un salvaje {username} apareció! �",
                "¡{username} se ha unido a la banda de aventureros! �",
                "¡{username} se apunta a la locura! ⚡"
            ],
            'level_up': [
                "¡{username} ahora es nivel {level}! ¡Sube como la espuma! 🎆",
                "¡Ding! ¡{username} acaba de evolucionar! 🎮",
                "¡{username} se ha convertido en leyenda! 👑"
            ]
        }

    async def send_batch_notifications(self, user_ids: List[int], message: str):
        """Envía notificaciones en lotes para evitar sobrecarga"""
        for i in range(0, len(user_ids), self.batch_size):
            batch = user_ids[i:i + self.batch_size]
            try:
                await self.bot.send_message(batch, message)
                logger.info(f"Notificación enviada a lote {i//self.batch_size + 1}")
            except Exception as e:
                logger.error(f"Error enviando notificaciones: {e}")

    async def notify_event(self, user: User, event_type: str, **kwargs):
        """Notifica un evento específico con humor personalizado"""
        template = random.choice(self.humor_messages.get(event_type, ["🎉 ¡Algo emocionante ocurrió!"]))
        message = template.format(username=user.full_name, **kwargs)
        
        try:
            await self.bot.send_message(user.id, f"🚀 ¡Noticia Épica!\n\n{message}")
            logger.info(f"Notificación de {event_type} enviada a {user.full_name}")
        except Exception as e:
            logger.error(f"Error notificando a {user.full_name}: {e}")

    async def send_admin_report(self, admin_id: int):
        """Envía un reporte administrativo con métricas"""
        stats = await self.db.get_admin_stats()
        message = (
            "⚙️ Panel de Administración\n\n"
            f"📊 Usuarios activos: {stats['active_users']}\n"
            f"🎯 Misiones completadas: {stats['completed_missions']}\n"
            f"🎁 Regalos distribuidos: {stats['gifts_sent']}\n"
            f"🛍️ Subastas finalizadas: {stats['auctions_ended']}\n\n"
            "🔨 Moderar   🚀 Notificar   🧹 Limpieza"
        )
        
        try:
            await self.bot.send_message(admin_id, message)
        except Exception as e:
            logger.error(f"Error enviando reporte admin a {admin_id}: {e}")