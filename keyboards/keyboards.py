"""
Sistema de teclados - Fase 2
Implementa menús de navegación adaptados por usuario
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any

class KeyboardBuilder:
    
    @staticmethod
    def main_menu(user_data: Dict[str, Any]) -> InlineKeyboardMarkup:
        """Construye el menú principal adaptado al usuario"""
        buttons = []
        
        # Fila 1: Botones principales
        buttons.append([
            InlineKeyboardButton(text="🏠 Inicio", callback_data="main_home"),
            InlineKeyboardButton(text="🎁 Regalo Diario", callback_data="daily_gift"),
            InlineKeyboardButton(text="🏆 Mi Perfil", callback_data="profile")
        ])
        
        # Fila 2: Canales
        buttons.append([
            InlineKeyboardButton(text="📺 Canales", callback_data="channels_list")
        ])
        
        # Fila 3: Opciones especiales según permisos
        special_row = []
        if user_data.get('is_vip'):
            special_row.append(
                InlineKeyboardButton(text="👑 VIP", callback_data="vip_menu")
            )
        
        if user_data.get('is_admin'):
            special_row.append(
                InlineKeyboardButton(text="⚙️ Admin", callback_data="admin_menu")
            )
        
        if special_row:
            buttons.append(special_row)
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def channels_menu(channels: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        """Construye el menú de canales disponibles"""
        buttons = []
        
        for channel in channels:
            channel_name = channel['name']
            channel_id = channel['channel_id']
            is_vip = channel['is_vip']
            
            # Icono según tipo
            icon = "👑" if is_vip else "🆓"
            action_text = "🔒 Acceso VIP" if is_vip else "🔓 Unirse"
            
            # Botón de canal
            buttons.append([
                InlineKeyboardButton(
                    text=f"{icon} {channel_name}",
                    callback_data=f"channel_info_{channel_id}"
                ),
                InlineKeyboardButton(
                    text=action_text,
                    callback_data=f"channel_join_{channel_id}"
                )
            ])
        
        # Navegación
        buttons.append([
            InlineKeyboardButton(text="🔙 Volver", callback_data="back_to_main")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        """Teclado simple de vuelta al menú principal"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver al Menú", callback_data="back_to_main")],
            [InlineKeyboardButton(text="🏠 Inicio", callback_data="main_home")]
        ])