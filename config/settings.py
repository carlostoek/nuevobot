from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///bot.db")
    admin_ids: str = os.getenv("ADMIN_IDS", "")
    debug: bool = os.getenv("DEBUG", "False") == "True"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
