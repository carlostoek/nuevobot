from .models import create_tables

async def run_migrations():
    await create_tables()
