from maxapi import Router
from maxapi.types import MessageCallback

from db.database import SessionLocal
from db.crud import get_user_by_max_id
from keyboards.inline import main_menu_keyboard

router = Router()


@router.message_callback()
async def callback_menu(event: MessageCallback):
    if event.callback.payload != "menu":
        return

    user_id = str(event.callback.user.user_id)

    db = SessionLocal()
    try:
        user = get_user_by_max_id(db, user_id)
        if not user or user.status != "approved":
            await event.callback.answer("Доступ не предоставлен.")
            return
    finally:
        db.close()

    await event.callback.answer("")
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="📋 Главное меню\nВыберите раздел:",
        attachments=[main_menu_keyboard()]
    )
