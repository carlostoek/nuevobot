# database/models.py
import aiosqlite
from datetime import datetime, date
from typing import Optional, Dict, Any
from config.settings import DATABASE_URL

class Database:
    def __init__(self):
        self.db_path = DATABASE_URL.replace("sqlite:///", "")
    
    async def init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    besitos INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    last_daily_gift DATE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.commit()
    
    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user by telegram_id"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE telegram_id = ?", 
                (telegram_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def create_user(self, telegram_id: int, username: str, first_name: str) -> Dict[str, Any]:
        """Create new user"""
        from config.settings import WELCOME_BESITOS
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO users (telegram_id, username, first_name, besitos, level)
                VALUES (?, ?, ?, ?, 1)
            """, (telegram_id, username, first_name, WELCOME_BESITOS))
            
            await db.commit()
            return await self.get_user(telegram_id)
    
    async def update_user_besitos(self, telegram_id: int, besitos: int) -> bool:
        """Update user besitos and level"""
        from config.settings import LEVEL_MULTIPLIER
        
        new_level = max(1, besitos // LEVEL_MULTIPLIER)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE users 
                SET besitos = ?, level = ?, updated_at = CURRENT_TIMESTAMP
                WHERE telegram_id = ?
            """, (besitos, new_level, telegram_id))
            
            await db.commit()
            return True
    
    async def claim_daily_gift(self, telegram_id: int) -> bool:
        """Claim daily gift if available"""
        from config.settings import DAILY_GIFT_BESITOS
        
        user = await self.get_user(telegram_id)
        if not user:
            return False
        
        today = date.today()
        last_gift = user.get('last_daily_gift')
        
        # Check if gift already claimed today
        if last_gift and str(today) == last_gift:
            return False
        
        # Add gift besitos
        new_besitos = user['besitos'] + DAILY_GIFT_BESITOS
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE users 
                SET besitos = ?, last_daily_gift = ?, updated_at = CURRENT_TIMESTAMP
                WHERE telegram_id = ?
            """, (new_besitos, today, telegram_id))
            
            await db.commit()
        
        # Update level
        await self.update_user_besitos(telegram_id, new_besitos)
        return True

# Global database instance
db = Database()