from datetime import datetime, timedelta
from database import get_db, User
from .gamification_service import GamificationService

class GiftService:
    def __init__(self):
        self.gamification = GamificationService()

    async def claim_daily_gift(self, user_id: int) -> bool:
        today = datetime.utcnow().date()
        with next(get_db()) as db:
            user = db.query(User).filter_by(id=user_id).first()
            if not user:
                return False
            if user.last_daily_gift == today:
                return False
            user.last_daily_gift = today
            db.commit()
            await self.gamification.add_besitos(user_id, 20, "daily_gift")
            return True
