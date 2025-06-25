from aiogram import Router, types, F
from aiogram.filters import Command
from digest import generate_digest, split_long_message
from utils.lang import t
from db.json_storage import load_messages
from db.group import get_group_lang
from asyncio import sleep
import time
from db.cooldown import set_cooldown, check_cooldown

router = Router()

@router.message(Command("digest"))
async def manual_digest(message: types.Message):
    lang = await get_group_lang(message.chat.id) or "eng"
    
    cooldown = await check_cooldown(message.chat.id, "digest")
    if cooldown > 0:
        hours = cooldown // 3600
        minutes = (cooldown % 3600) // 60
        await message.answer(
            t("digest_cooldown", lang).format(hours=hours, minutes=minutes)
        )
        return

    messages = load_messages()
    chat_msg_count = len([msg for msg in messages if msg.get("chat_id") == message.chat.id])

    if chat_msg_count < 100:
        await message.answer(
            t("not_enough_messages", lang,
              count=chat_msg_count,
              needed=100 - chat_msg_count)
        )
        return

    await message.answer(t("digest_generating", lang))

    try:
        digest = await generate_digest(message.chat.id)
        if digest:
            await set_cooldown(message.chat.id, "digest", 14400)
            
            message_parts = await split_long_message(digest)
            first_message_sent = False
            for part in message_parts:
                sent_message = await message.answer(part)
                if not first_message_sent:
                    await message.bot.pin_chat_message(
                        chat_id=message.chat.id,
                        message_id=sent_message.message_id,
                        disable_notification=True
                    )
                    first_message_sent = True
                await sleep(0.5)
    except Exception as e:
        await message.answer(t("digest_error", lang))
        print(f"[manual_digest] error in {message.chat.id}: {e}")