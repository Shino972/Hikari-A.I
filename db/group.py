import aiosqlite

async def add_group(chat_id: int, lang: str = "eng"):
    async with aiosqlite.connect("groups.db") as db:
        await db.execute("""
            INSERT INTO groups (chat_id, lang)
            VALUES (?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                lang = excluded.lang,
                active = 1
        """, (chat_id, lang))
        await db.commit()