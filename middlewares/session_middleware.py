# middlewares/session_middleware.py - EXTENSIÓN FASE 4

from typing import Dict, Any, List, Optional, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update
from dataclasses import dataclass, field
import time

@dataclass
class SessionData:
    """Datos de sesión del usuario extendidos para Fase 4"""
    user_id: int = 0
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    language_code: str = "es"
    
    # Estados de navegación
    current_menu: str = "main"
    previous_menu: str = "main"
    
    # Sistema de combate (Fase 3)
    in_combat: bool = False
    combat_enemy: Optional[str] = None
    combat_turn: int = 0
    
    # NUEVOS: Sistema narrativo (Fase 4)
    combining_lore: List[int] = field(default_factory=list)
    viewing_lore_id: Optional[int] = None
    
    # NUEVOS: Sistema de minijuegos (Fase 4)
    active_minigame: Optional[str] = None
    minigame_start_time: Optional[float] = None
    trivia_question_id: Optional[int] = None
    trivia_current_question: int = 0
    trivia_score: int = 0
    trivia_correct_answers: int = 0
    
    # Control de tiempo
    last_activity: float = field(default_factory=time.time)
    session_timeout: int = 1800  # 30 minutos
    
    def is_expired(self) -> bool:
        """Verifica si la sesión ha expirado"""
        return time.time() - self.last_activity > self.session_timeout
    
    def update_activity(self):
        """Actualiza la última actividad"""
        self.last_activity = time.time()
    
    def reset_combat(self):
        """Reinicia datos de combate"""
        self.in_combat = False
        self.combat_enemy = None
        self.combat_turn = 0
    
    def reset_lore_combination(self):
        """Reinicia datos de combinación de lore"""
        self.combining_lore = []
        self.viewing_lore_id = None
    
    def reset_minigame(self):
        """Reinicia datos de minijuego"""
        self.active_minigame = None
        self.minigame_start_time = None
        self.trivia_question_id = None
        self.trivia_current_question = 0
        self.trivia_score = 0
        self.trivia_correct_answers = 0
    
    def start_minigame(self, game_type: str):
        """Inicia un nuevo minijuego"""
        self.reset_minigame()
        self.active_minigame = game_type
        self.minigame_start_time = time.time()
    
    def get_minigame_duration(self) -> float:
        """Obtiene duración del minijuego actual"""
        if not self.minigame_start_time:
            return 0.0
        return time.time() - self.minigame_start_time
    
    def navigate_to(self, menu: str):
        """Navega a un menú específico"""
        self.previous_menu = self.current_menu
        self.current_menu = menu
        self.update_activity()
    
    def go_back(self):
        """Regresa al menú anterior"""
        current = self.current_menu
        self.current_menu = self.previous_menu
        self.previous_menu = current
        self.update_activity()

class SessionMiddleware(BaseMiddleware):
    """Middleware de gestión de sesiones extendido"""
    
    def __init__(self):
        self.sessions: Dict[int, SessionData] = {}
        self.cleanup_interval = 3600  # Limpiar cada hora
        self.last_cleanup = time.time()
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        user = None
        
        # Obtener usuario del evento
        if event.message:
            user = event.message.from_user
        elif event.callback_query:
            user = event.callback_query.from_user
        elif event.inline_query:
            user = event.inline_query.from_user
        
        if not user:
            return await handler(event, data)
        
        # Limpiar sesiones expiradas periódicamente
        if time.time() - self.last_cleanup > self.cleanup_interval:
            self._cleanup_expired_sessions()
        
        # Obtener o crear sesión
        session = self.get_or_create_session(user)
        
        # Verificar expiración
        if session.is_expired():
            # Limpiar datos de sesión pero mantener info básica
            session.reset_combat()
            session.reset_lore_combination()
            session.reset_minigame()
            session.current_menu = "main"
            session.previous_menu = "main"
        
        # Actualizar actividad
        session.update_activity()
        
        # Pasar sesión al handler
        data["session"] = session
        
        return await handler(event, data)
    
    def get_or_create_session(self, user) -> SessionData:
        """Obtiene o crea una sesión para el usuario"""
        if user.id not in self.sessions:
            self.sessions[user.id] = SessionData(
                user_id=user.id,
                username=user.username or "",
                first_name=user.first_name or "",
                last_name=user.last_name or "",
                language_code=user.language_code or "es"
            )
        
        return self.sessions[user.id]
    
    def _cleanup_expired_sessions(self):
        """Limpia sesiones expiradas"""
        current_time = time.time()
        expired_users = []
        
        for user_id, session in self.sessions.items():
            if session.is_expired():
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del self.sessions[user_id]
        
        self.last_cleanup = current_time
    
    def get_session(self, user_id: int) -> Optional[SessionData]:
        """Obtiene sesión específica"""
        return self.sessions.get(user_id)
    
    def clear_session(self, user_id: int):
        """Limpia sesión específica"""
        if user_id in self.sessions:
            del self.sessions[user_id]