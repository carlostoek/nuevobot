from database.models import VIPToken
from database.database import async_session
from datetime import datetime, timedelta
import uuid
from config import VIP_TOKEN_EXPIRY_DAYS

class TokenService:
    @staticmethod
    async def generate_vip_token(user_id):
        token_str = str(uuid.uuid4())
        expiry = datetime.utcnow() + timedelta(days=VIP_TOKEN_EXPIRY_DAYS)
        async with async_session() as session:
            vip_token = VIPToken(user_id=user_id, token=token_str, expiry_date=expiry)
            session.add(vip_token)
            await session.commit()
        return vip_token

    @staticmethod
    async def validate_token(token_str):
        async with async_session() as session:
            token = await session.get(VIPToken, {'token': token_str})
            if token and token.expiry_date > datetime.utcnow():
                return True
            return False