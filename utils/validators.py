from aiogram.types import Message

async def is_admin(message: Message) -> bool:
    from middlewares import UserContext
    user_ctx: UserContext = message.conf.get('user_context')  # Aiogram v3 config
    return user_ctx.is_admin if user_ctx else False
