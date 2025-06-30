import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    BOT_TOKEN: str
    DATABASE_URL: str
    ADMIN_IDS: List[int]
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    DB_POOL_SIZE: int = 5
    DB_TIMEOUT: int = 30
    CACHE_TTL: int = 300

def get_settings() -> Settings:
    admin_ids = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
    return Settings(
        BOT_TOKEN=os.getenv("BOT_TOKEN", ""),
        DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///bot.db"),
        ADMIN_IDS=admin_ids,
        DEBUG=os.getenv("DEBUG", "False").lower() == "true",
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
    )
