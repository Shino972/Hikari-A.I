import json
from pathlib import Path
import asyncio
import math
import time
from asyncio import sleep
from openai import AsyncOpenAI
from aiogram import Bot


from db.group import get_group_style
from config import PROMPT_STYLES

from db.group import get_group_lang
from db.json_storage import clear_processed_messages, load_messages
from config import OPENAI_API_KEY, OPENAI_BASE_URL

async def calculate_digest_time(chat_id: int) -> float:
    from db.group import get_group_add_time
    
    add_time = await get_group_add_time(chat_id)
    if add_time is None:
        return 0
    
    offset = (chat_id % 86400)
    
    now = time.time()
    
    next_digest = math.floor((now - add_time) / 86400) * 86400 + add_time + offset
    
    if next_digest < now:
        next_digest += 86400
    
    return next_digest

async def split_long_message(message: str, max_length: int = 4096) -> list[str]:
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]

async def generate_digest(chat_id: int):
    messages = load_messages()
    chat_messages = [msg for msg in messages if msg.get("chat_id") == chat_id]
    
    if len(chat_messages) < 100:
        return None
    
    lang = await get_group_lang(chat_id)
    style = await get_group_style(chat_id) or "default"
    
    prompt_file = f"prompts/{PROMPT_STYLES[style]['files'][lang]}"
    
    if not Path(prompt_file).exists():
        prompt_file = f"prompts/prompt_{lang}.txt"
        if not Path(prompt_file).exists():
            prompt_file = "prompts/prompt_eng.txt"

    def sanitize_message(msg):
        sanitized = msg.copy()
        sanitized.pop("chat_id", None)
        sanitized.pop("user_id", None)
        if "reply_to" in sanitized and isinstance(sanitized["reply_to"], dict):
            sanitized["reply_to"].pop("user_id", None)
        return sanitized

    sanitized_messages = [sanitize_message(msg) for msg in chat_messages]
    
    client = AsyncOpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL
    )

    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_text = f.read()

    messages = [
        {"role": "system", "content": prompt_text},
        {"role": "user", "content": json.dumps(sanitized_messages, ensure_ascii=False)}
    ]

    response = await client.chat.completions.create(
        model="google/gemini-2.0-flash-exp:free",
        messages=messages,
        temperature=1.0,
        top_p=0.95,
        max_tokens=8192
    )
    clear_processed_messages(chat_id)
    return response.choices[0].message.content

async def digest_scheduler(bot: Bot):
    while True:
        await asyncio.sleep(86400)
        from db.group import get_active_groups
        
        active_groups = await get_active_groups()
        for chat_id in active_groups:
            try:
                digest = await generate_digest(chat_id)
                if digest:
                    message_parts = await split_long_message(digest)
                    first_message_sent = False
                    for part in message_parts:
                        sent_message = await bot.send_message(chat_id, part)
                        if not first_message_sent:
                            try:
                                await bot.pin_chat_message(
                                    chat_id=chat_id,
                                    message_id=sent_message.message_id,
                                    disable_notification=False
                                )
                                first_message_sent = True
                            except Exception as pin_error:
                                print(f"Failed to pin message: {pin_error}")
                                first_message_sent = True
                        await sleep(0.5)
            except Exception as e:
                print(f"[digest_scheduler] error in {chat_id}: {e}")