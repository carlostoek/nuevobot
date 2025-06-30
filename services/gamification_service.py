from datetime import datetime
from database import get_db, User

class GamificationService:
    async def add_besitos(self, user_id: int, amount: int, reason: str) -> int:
        with next(get_db()) as db:
            user = db.query(User).filter_by(id=user_id).first()
            if not user:
                return 0
            user.besitos += amount
            user.level = self.calculate_level(user.besitos)
            db.commit()
            db.refresh(user)
            return user.besitos

    def calculate_level(self, besitos: int) -> int:
        # Simple progression: 100 besitos per level
        return max(1, besitos // 100 + 1)
