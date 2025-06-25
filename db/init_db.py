import aiosqlite

async def init_db():
    async with aiosqlite.connect("users.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                lang TEXT DEFAULT 'eng'
            )
        """)
        await db.commit()

    async with aiosqlite.connect("groups.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                chat_id INTEGER PRIMARY KEY,
                active BOOLEAN DEFAULT 1,
                lang TEXT DEFAULT 'eng',
                topic TEXT DEFAULT NULL
            );
        """)
        await db.commit()