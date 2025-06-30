from datetime import datetime, timedelta
from typing import List
from database import get_db, Mission, UserMission
from .gamification_service import GamificationService

class MissionService:
    def __init__(self):
        self.gamification = GamificationService()

    async def assign_daily_mission(self, user_id: int) -> UserMission:
        with next(get_db()) as db:
            mission = db.query(Mission).filter(Mission.expires_at > datetime.utcnow()).first()
            if not mission:
                mission = Mission(
                    name="El Desafío Diario",
                    description="Visita 3 canales diferentes",
                    reward_besitos=50,
                    expires_at=datetime.utcnow() + timedelta(hours=24)
                )
                db.add(mission)
                db.commit()
                db.refresh(mission)
            user_mission = UserMission(user_id=user_id, mission_id=mission.id)
            db.add(user_mission)
            db.commit()
            db.refresh(user_mission)
            return user_mission

    async def complete_mission(self, user_mission_id: int):
        with next(get_db()) as db:
            um = db.query(UserMission).filter_by(id=user_mission_id, completed=False).first()
            if not um:
                return
            um.completed = True
            db.commit()
            await self.gamification.add_besitos(um.user_id, um.mission.reward_besitos, "mission")

    async def get_user_missions(self, user_id: int) -> List[UserMission]:
        with next(get_db()) as db:
            return db.query(UserMission).filter_by(user_id=user_id).all()
