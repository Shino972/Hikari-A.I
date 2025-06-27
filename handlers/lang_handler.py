from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ChatMemberStatus
from utils.lang import t
from db.group import get_group_lang

router = Router()

async def check_user_permissions(bot, chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            return True
        
        return False
    except Exception:
        return False

@router.message(Command("lang"))
async def change_lang_command(message: types.Message):
    lang = await get_group_lang(message.chat.id) or "eng"
    
    has_permission = await check_user_permissions(message.bot, message.chat.id, message.from_user.id)
    if not has_permission:
        return
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🇷🇺 Русский", callback_data="set_lang_rus")
    kb.button(text="🇬🇧 English", callback_data="set_lang_eng")
    kb.button(text="🇨🇳 中文", callback_data="set_lang_chi")
    kb.adjust(2, 1)
    
    await message.reply(t("lang_change_prompt", lang), reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("set_lang_"))
async def set_lang_callback(callback: types.CallbackQuery):
    lang_code = callback.data.split("_")[2]
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    
    has_permission = await check_user_permissions(callback.bot, chat_id, user_id)
    if not has_permission:
        lang = await get_group_lang(chat_id) or "eng"
        return
    
    from db.group import add_group
    await add_group(chat_id, lang_code)
    
    await callback.message.edit_text(
        t("lang_change_success", lang_code),
        reply_markup=None
    )
    await callback.answer()