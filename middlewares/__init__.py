from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class UserContext:
    user_id: int
    telegram_id: int
    username: str
    is_admin: bool
    is_vip: bool
    besitos: int
    level: int
    session_data: Dict[str, Any] = field(default_factory=dict)

__all__ = ['UserContext']
