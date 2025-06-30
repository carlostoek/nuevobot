from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """Modelo del usuario del bot"""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    besitos: int = 100
    nivel: int = 1
    experiencia: int = 0
    last_daily_reward: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()

@dataclass
class Channel:
    """Modelo del canal"""
    channel_id: int
    channel_name: str
    channel_username: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class UserChannel:
    """Relación muchos a muchos entre usuarios y canales"""
    user_telegram_id: int
    channel_id: int
    joined_at: Optional[datetime] = None
    is_member: bool = True
    
    def __post_init__(self):
        if self.joined_at is None:
            self.joined_at = datetime.now()