from typing import Optional
from sqlalchemy.orm import Session

from database import get_db, User
from config import get_settings

settings = get_settings()

class UserService:
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        with next(get_db()) as db:
            return db.query(User).filter_by(telegram_id=telegram_id).first()

    async def create_user(self, telegram_id: int, username: str, first_name: str) -> User:
        with next(get_db()) as db:
            user = User(telegram_id=telegram_id, username=username, first_name=first_name)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user

    async def update_besitos(self, user_id: int, amount: int) -> User:
        with next(get_db()) as db:
            user = db.query(User).filter_by(id=user_id).first()
            if user:
                user.besitos += amount
                db.commit()
                db.refresh(user)
            return user

    async def get_user_level(self, user_id: int) -> int:
        with next(get_db()) as db:
            user = db.query(User).filter_by(id=user_id).first()
            return user.level if user else 0

    async def is_user_admin(self, user_id: int) -> bool:
        return user_id in settings.ADMIN_IDS

    async def is_user_vip(self, user_id: int) -> bool:
        with next(get_db()) as db:
            user = db.query(User).filter_by(id=user_id).first()
            return bool(user and user.vip_status)
