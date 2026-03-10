from maxapi import Bot, Router
from maxapi.types import MessageCreated, MessageCallback, Command

from db.database import SessionLocal
from db.crud import get_user_by_max_id, create_user, update_user_fields
from keyboards.inline import make_keyboard, main_menu_keyboard
from states.forms import RegistrationState

router = Router()

# In-memory FSM store: {user_id: {"state": ..., "data": {...}}}
_user_states: dict[str, dict] = {}


def _get_state(user_id: str) -> str | None:
    return _user_states.get(user_id, {}).get("state")


def _set_state(user_id: str, state: str | None, **data):
    if state is None:
        _user_states.pop(user_id, None)
    else:
        if user_id not in _user_states:
            _user_states[user_id] = {"state": state, "data": {}}
        _user_states[user_id]["state"] = state
        _user_states[user_id]["data"].update(data)


def _get_data(user_id: str) -> dict:
    return _user_states.get(user_id, {}).get("data", {})


@router.message_created(Command("start"))
async def cmd_start(event: MessageCreated):
    user_id = str(event.message.sender.user_id)
    username = event.message.sender.username or ""

    db = SessionLocal()
    try:
        user = get_user_by_max_id(db, user_id)

        if user is None:
            # New user — start registration
            await event.message.answer(
                "⚠️ Бот доступен только сотрудникам компании.\n\n"
                "Для получения доступа пройдите регистрацию.\n"
                "Введите ваше ФИО:"
            )
            _set_state(user_id, RegistrationState.WAITING_FULL_NAME, username=username)
            return

        if user.status == "pending":
            await event.message.answer(
                "Вы уже отправили данные, доступ будет выдан в течение дня."
            )
            return

        if user.status == "blocked":
            await event.message.answer("Доступ заблокирован. Обратитесь к администратору.")
            return

        # approved — show welcome + menu button
        name = user.full_name or username or "пользователь"
        await event.message.answer(
            f"Привет, {name}! Я бот техподдержки Finbox.\n"
            "Здесь вы найдёте памятки, инструкции, обучающие материалы и другую полезную информацию.",
            attachments=[make_keyboard([
                [{"text": "🟢 Меню", "callback": "menu"}]
            ])]
        )
    finally:
        db.close()


@router.message_created()
async def handle_text_input(event: MessageCreated):
    """Handle FSM text inputs for registration."""
    user_id = str(event.message.sender.user_id)
    state = _get_state(user_id)

    if state == RegistrationState.WAITING_FULL_NAME:
        full_name = (event.message.body or {}).get("text", "").strip()
        if not full_name:
            await event.message.answer("Пожалуйста, введите ваше ФИО:")
            return
        _set_state(user_id, RegistrationState.WAITING_CONTACT, full_name=full_name)
        await event.message.answer(
            "Отправьте ваш контакт для завершения регистрации:",
            attachments=[make_keyboard([
                [{"text": "📱 Отправить контакт", "request_contact": True}]
            ])]
        )
        return

    # If no FSM state, ignore (other handlers will process)


@router.message_created()
async def handle_contact(event: MessageCreated):
    """Handle contact sharing for registration."""
    user_id = str(event.message.sender.user_id)
    state = _get_state(user_id)

    if state != RegistrationState.WAITING_CONTACT:
        return

    # Extract contact info from message
    body = event.message.body or {}
    contact = body.get("contact")
    phone = ""
    if contact:
        phone = contact.get("phone", "")
    elif body.get("text"):
        # Fallback: user typed phone manually
        phone = body["text"].strip()

    data = _get_data(user_id)
    full_name = data.get("full_name", "")
    username = data.get("username", "")

    db = SessionLocal()
    try:
        existing = get_user_by_max_id(db, user_id)
        if existing is None:
            create_user(db, max_user_id=user_id, username=username, full_name=full_name, phone=phone, status="pending")
        else:
            update_user_fields(db, existing, full_name=full_name, phone=phone)
    finally:
        db.close()

    _set_state(user_id, None)
    await event.message.answer(
        "✅ Данные приняты, доступ будет предоставлен в течение дня."
    )
