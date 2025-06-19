# criar_tabelas.py

import asyncio
from models import Base
from database import engine

async def criar_tabelas():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(criar_tabelas())
print("✅ Tabelas criadas com sucesso.")
