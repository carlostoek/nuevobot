from typing import List, Optional
from sqlalchemy.orm import Session

from database import get_db, Channel, UserChannel

class ChannelService:
    async def create_channel(self, name: str) -> Channel:
        with next(get_db()) as db:
            channel = Channel(name=name)
            db.add(channel)
            db.commit()
            db.refresh(channel)
            return channel

    async def list_channels(self) -> List[Channel]:
        with next(get_db()) as db:
            return db.query(Channel).all()

    async def add_user_to_channel(self, user_id: int, channel_id: int) -> UserChannel:
        with next(get_db()) as db:
            link = UserChannel(user_id=user_id, channel_id=channel_id)
            db.add(link)
            db.commit()
            db.refresh(link)
            return link

    async def user_in_channel(self, user_id: int, channel_id: int) -> bool:
        with next(get_db()) as db:
            return bool(db.query(UserChannel).filter_by(user_id=user_id, channel_id=channel_id).first())
