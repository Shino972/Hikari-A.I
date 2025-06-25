import aiosqlite

async def add_user(user_id: int):
    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        exists = await cursor.fetchone()
        if not exists:
            await db.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
            await db.commit()

async def set_user_lang(user_id: int, lang: str):
    async with aiosqlite.connect("users.db") as db:
        await db.execute("UPDATE users SET lang = ? WHERE id = ?", (lang, user_id))
        await db.commit()

async def get_user_lang(user_id: int) -> str:
    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute("SELECT lang FROM users WHERE id = ?", (user_id,))
        result = await cursor.fetchone()
        return result[0] if result else "eng"
