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

generating_digests = {}

@router.message(Command("digest"))
async def manual_digest(message: types.Message):
    lang = await get_group_lang(message.chat.id) or "eng"

    if generating_digests.get(message.chat.id, False):
        return

    cooldown = await check_cooldown(message.chat.id, "digest")
    if cooldown > 0:
        hours = cooldown // 3600
        minutes = (cooldown % 3600) // 60
        await message.answer(
            t("digest_cooldown", lang).format(hours=hours, minutes=minutes)
        )
        return

    messages = load_messages()
    chat_messages = [msg for msg in messages if msg.get("chat_id") == message.chat.id]
    chat_msg_count = len(chat_messages)

    if chat_msg_count < 100:
        await message.answer(
            t("not_enough_messages", lang,
              count=chat_msg_count,
              needed=100 - chat_msg_count)
        )
        return

    generating_digests[message.chat.id] = True

    generating_message = await message.answer(t("digest_generating", lang))

    try:
        digest = await generate_digest(message.chat.id)
        if not digest or not digest.strip():
            await message.answer(t("digest_empty", lang))
            return

        await set_cooldown(message.chat.id, "digest", 14400)
        
        message_parts = await split_long_message(digest)
        if not message_parts:
            await message.answer(t("digest_empty", lang))
            return

        first_message_sent = False
        for part in message_parts:
            if not part.strip():
                continue
                
            try:
                sent_message = await message.answer(part) 
                if not first_message_sent:
                    try:
                        await message.bot.pin_chat_message(
                            chat_id=message.chat.id,
                            message_id=sent_message.message_id,
                            disable_notification=False
                        )
                        first_message_sent = True
                    except Exception as pin_error:
                        print(f"Failed to pin message: {pin_error}")
                        first_message_sent = True
                await sleep(0.5)
            except Exception as send_error:
                print(f"Failed to send message part: {send_error}")
                continue
        
        await generating_message.delete()
        
    except Exception as e:
        print(f"[manual_digest] error in {message.chat.id}: {e}")
        await message.answer(t("digest_error", lang))
    finally:
        generating_digests.pop(message.chat.id, None)