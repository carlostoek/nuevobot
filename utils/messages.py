"""
Plantillas de mensajes - Fase 2
Mensajes personalizados y de error
"""
from typing import Dict, Any, List

class Messages:
    
    @staticmethod
    def welcome_message(user_data: Dict[str, Any]) -> str:
        """Mensaje de bienvenida personalizado"""
        first_name = user_data.get('first_name', 'Aventurero')
        besitos = user_data.get('besitos', 0)
        level = user_data.get('level', 1)
        
        return f"""🎉 ¡Bienvenido de vuelta, {first_name}!

🏆 Tu perfil ha sido restaurado con éxito.
💖 Saldo actual: {besitos} besitos.
⭐ Nivel: {level}

📺 Explora los canales disponibles y gana más besitos."""
    
    @staticmethod
    def new_user_welcome(user_data: Dict[str, Any]) -> str:
        """Mensaje de bienvenida para nuevos usuarios"""
        first_name = user_data.get('first_name', 'Aventurero')
        besitos = user_data.get('besitos', 100)
        
        return f"""🎊 ¡Bienvenido al Bot, {first_name}!

🎁 Has recibido {besitos} besitos de bienvenida.
⭐ Comenzaste en el nivel 1.

📺 Únete a los canales disponibles para ganar más besitos.
🏆 ¡Completa tu perfil y comienza tu aventura!"""
    
    @staticmethod
    def profile_info(user_data: Dict[str, Any]) -> str:
        """Información del perfil del usuario"""
        username = user_data.get('username', 'Sin username')
        first_name = user_data.get('first_name', 'Sin nombre')
        besitos = user_data.get('besitos', 0)
        level = user_data.get('level', 1)
        is_vip = user_data.get('is_vip', False)
        is_admin = user_data.get('is_admin', False)
        
        vip_status = "👑 VIP Activo" if is_vip else "🆓 Usuario Regular"
        admin_badge = "\n⚙️ **ADMINISTRADOR**" if is_admin else ""
        
        return f"""🏆 **Tu Perfil**

👤 **Nombre:** {first_name}
🏷️ **Username:** @{username}
💖 **Besitos:** {besitos}
⭐ **Nivel:** {level}
🎯 **Estado:** {vip_status}{admin_badge}

💡 **Tip:** Únete a más canales para ganar besitos extra."""
    
    @staticmethod
    def channels_list_header(channels: List[Dict[str, Any]]) -> str:
        """Cabecera de la lista de canales"""
        total_channels = len(channels)
        vip_channels = sum(1 for c in channels if c.get('is_vip'))
        free_channels = total_channels - vip_channels
        
        return f"""📺 **Lista de Canales Disponibles**

🆓 Canales gratuitos: {free_channels}
👑 Canales VIP: {vip_channels}

💡 Únete para ganar besitos por cada canal."""
    
    @staticmethod
    def error_channel_not_found() -> str:
        """Error cuando no se encuentra un canal"""
        return "❌ Canal no encontrado o no disponible."
    
    @staticmethod
    def error_vip_required() -> str:
        """Error cuando se requiere VIP"""
        return "👑 Este canal requiere acceso VIP. ¡Hazte VIP para acceder!"
    
    @staticmethod
    def success_channel_joined(channel_name: str, reward: int) -> str:
        """Éxito al unirse a un canal"""
        return f"""✅ **¡Te has unido exitosamente!**

📺 Canal: {channel_name}
🎁 Recompensa: +{reward} besitos

¡Gracias por unirte a nuestra comunidad!"""