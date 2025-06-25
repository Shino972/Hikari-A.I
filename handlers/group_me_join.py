from aiogram import types, Router
from aiogram.enums import ChatType
from db.user import get_user_lang
from db.group import add_group

from utils.lang import t

router = Router()

@router.my_chat_member()
async def group_me_welcome(event: types.ChatMemberUpdated):
    try:
        if event.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            user_id = event.from_user.id
            chat_id = event.chat.id
            
            lang = await get_user_lang(user_id)

            if not lang:
                lang = "eng"
            
            await add_group(chat_id, lang)
            
            await event.bot.send_message(
                chat_id=event.chat.id,
                text=t("group_me_welcome", lang, 
                        first_name=event.from_user.first_name, user_id=user_id),
                disable_notification=True
            )

    except Exception as e:
        print(e)