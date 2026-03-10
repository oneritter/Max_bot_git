from maxapi import Router
from maxapi.types import MessageCreated, MessageCallback

from db.database import SessionLocal
from db.crud import get_user_by_max_id, create_feedback
from keyboards.inline import make_keyboard, back_and_menu
from states.forms import FeedbackState

router = Router()

_feedback_states: dict[str, dict] = {}


def _get_state(uid: str) -> str | None:
    return _feedback_states.get(uid, {}).get("state")


def _set_state(uid: str, state: str | None):
    if state is None:
        _feedback_states.pop(uid, None)
    else:
        _feedback_states[uid] = {"state": state}


# --- "Нет нужной информации" ---

@router.message_callback()
async def cb_no_info(event: MessageCallback):
    if event.callback.payload != "no_info":
        return
    await event.callback.answer("")

    uid = str(event.callback.user.user_id)
    _set_state(uid, FeedbackState.WAITING_QUESTION)
    await event.bot.send_message(
        chat_id=event.chat_id,
        text=(
            "❓ Не нашли нужную информацию?\n\n"
            "Напишите ваш вопрос, и с вами свяжутся в ближайшее время.\n"
            "Или нажмите «Меню» для возврата."
        ),
        attachments=[make_keyboard([
            [{"text": "🟢 Меню", "callback": "menu"}]
        ])]
    )


@router.message_created()
async def handle_feedback_text(event: MessageCreated):
    uid = str(event.message.sender.user_id)
    state = _get_state(uid)

    if state != FeedbackState.WAITING_QUESTION:
        return

    text = (event.message.body or {}).get("text", "").strip()
    if not text:
        return

    db = SessionLocal()
    try:
        user = get_user_by_max_id(db, uid)
        user_id = user.id if user else None
        create_feedback(db, user_id=user_id, question=text)
    finally:
        db.close()

    _set_state(uid, None)
    await event.message.answer(
        "✅ Спасибо за ваш вопрос! С вами свяжутся в ближайшее время.",
        attachments=[make_keyboard([
            [{"text": "🟢 Меню", "callback": "menu"}]
        ])]
    )


# --- "Предложить идею" ---

@router.message_callback()
async def cb_idea(event: MessageCallback):
    if event.callback.payload != "idea":
        return
    await event.callback.answer("")
    kb = make_keyboard([
        [{"text": "💬 Написать", "url": "https://t.me/run_ritter_run"}],
        *back_and_menu("menu"),
    ])
    await event.bot.send_message(
        chat_id=event.chat_id,
        text=(
            "💡 Предложить идею\n\n"
            "Есть идея, как улучшить работу? Напишите нам!\n"
            "Мы открыты к предложениям и всегда рады обратной связи."
        ),
        attachments=[kb]
    )
