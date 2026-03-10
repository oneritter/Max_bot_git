import re
from maxapi import Router
from maxapi.types import MessageCreated, MessageCallback

from db.database import SessionLocal
from db.crud import get_user_by_max_id, create_training_request
from keyboards.inline import make_keyboard, back_and_menu
from states.forms import TrainingFormState
from services.sheets import append_training_request

router = Router()

# In-memory FSM for training form
_train_states: dict[str, dict] = {}


def _get_state(uid: str) -> str | None:
    return _train_states.get(uid, {}).get("state")


def _set_state(uid: str, state: str | None, **data):
    if state is None:
        _train_states.pop(uid, None)
    else:
        if uid not in _train_states:
            _train_states[uid] = {"state": state, "data": {}}
        _train_states[uid]["state"] = state
        _train_states[uid]["data"].update(data)


def _get_data(uid: str) -> dict:
    return _train_states.get(uid, {}).get("data", {})


# --- Callbacks ---

@router.message_callback()
async def cb_education(event: MessageCallback):
    payload = event.callback.payload
    if payload != "education":
        return

    await event.callback.answer("")
    kb = make_keyboard([
        [{"text": "📅 График обучения операторов", "callback": "edu_schedule"}],
        [{"text": "👤 Обучение нового ТМ", "callback": "edu_new_tm"}],
        [{"text": "✏️ Записаться на обучение вне графика", "callback": "edu_form_start"}],
        *back_and_menu("menu"),
    ])
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="🎓 Обучение ТМ / операторов",
        attachments=[kb]
    )


@router.message_callback()
async def cb_edu_schedule(event: MessageCallback):
    if event.callback.payload != "edu_schedule":
        return
    await event.callback.answer("")
    kb = make_keyboard([
        [{"text": "📊 Открыть график", "url": "https://docs.google.com/spreadsheets/d/1des_pqCjlI7E1Yyvd_qXyqRcqRzGik4qAk8r2bOWwUE"}],
        [{"text": "✏️ Записаться вне графика", "callback": "edu_form_start"}],
        *back_and_menu("education"),
    ])
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="📅 График обучения операторов",
        attachments=[kb]
    )


@router.message_callback()
async def cb_edu_new_tm(event: MessageCallback):
    if event.callback.payload != "edu_new_tm":
        return
    await event.callback.answer("")
    kb = make_keyboard([
        [{"text": "👩‍🏫 Связаться с куратором", "url": "https://t.me/anna_kropacheva_80"}],
        *back_and_menu("education"),
    ])
    await event.bot.send_message(
        chat_id=event.chat_id,
        text=(
            "👤 Обучение нового ТМ\n\n"
            "Для прохождения обучения свяжитесь с куратором.\n"
            "Куратор предоставит все необходимые материалы и график."
        ),
        attachments=[kb]
    )


@router.message_callback()
async def cb_edu_form_start(event: MessageCallback):
    if event.callback.payload != "edu_form_start":
        return
    await event.callback.answer("")
    uid = str(event.callback.user.user_id)
    _set_state(uid, TrainingFormState.WAITING_PARTNER_NAME)
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="✏️ Запись на обучение\n\nШаг 1/6: Введите название партнёра:"
    )


# --- FSM text handlers ---

@router.message_created()
async def handle_training_form(event: MessageCreated):
    uid = str(event.message.sender.user_id)
    state = _get_state(uid)

    if state is None or not str(state).startswith("train:"):
        return

    text = (event.message.body or {}).get("text", "").strip()

    if state == TrainingFormState.WAITING_PARTNER_NAME:
        if not text:
            await event.message.answer("Введите название партнёра:")
            return
        _set_state(uid, TrainingFormState.WAITING_SURNAME, partner_name=text)
        await event.message.answer("Шаг 2/6: Укажите фамилию:")

    elif state == TrainingFormState.WAITING_SURNAME:
        if not text:
            await event.message.answer("Укажите фамилию:")
            return
        _set_state(uid, TrainingFormState.WAITING_PHONE, surname=text)
        await event.message.answer(
            "Шаг 3/6: Отправьте ваш контакт или введите номер телефона:",
            attachments=[make_keyboard([
                [{"text": "📱 Отправить контакт", "request_contact": True}]
            ])]
        )

    elif state == TrainingFormState.WAITING_PHONE:
        # Accept contact or typed phone
        body = event.message.body or {}
        contact = body.get("contact")
        phone = contact.get("phone", "") if contact else text
        if not phone:
            await event.message.answer("Введите номер телефона:")
            return
        _set_state(uid, TrainingFormState.WAITING_TOPIC, phone=phone)
        await event.message.answer("Шаг 4/6: Укажите тему обучения:")

    elif state == TrainingFormState.WAITING_TOPIC:
        if not text:
            await event.message.answer("Укажите тему обучения:")
            return
        _set_state(uid, TrainingFormState.WAITING_DATE, topic=text)
        await event.message.answer("Шаг 5/6: Укажите дату (ДД.ММ.ГГГГ):")

    elif state == TrainingFormState.WAITING_DATE:
        if not text:
            await event.message.answer("Укажите дату (ДД.ММ.ГГГГ):")
            return
        _set_state(uid, TrainingFormState.WAITING_TIME, date=text)
        await event.message.answer("Шаг 6/6: Укажите время (ЧЧ:ММ):")

    elif state == TrainingFormState.WAITING_TIME:
        if not text or not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", text):
            await event.message.answer("Введите время в формате ЧЧ:ММ (например, 14:30):")
            return

        data = _get_data(uid)
        data["time"] = text

        # Save to DB
        db = SessionLocal()
        try:
            user = get_user_by_max_id(db, uid)
            user_id = user.id if user else None
            create_training_request(
                db,
                user_id=user_id,
                partner_name=data.get("partner_name", ""),
                surname=data.get("surname", ""),
                phone=data.get("phone", ""),
                topic=data.get("topic", ""),
                date=data.get("date", ""),
                time=data["time"],
            )
        finally:
            db.close()

        # Save to Google Sheets
        try:
            append_training_request(
                partner_name=data.get("partner_name", ""),
                surname=data.get("surname", ""),
                phone=data.get("phone", ""),
                topic=data.get("topic", ""),
                date=data.get("date", ""),
                time=data["time"],
            )
        except Exception:
            pass  # Don't block user if Sheets fails

        _set_state(uid, None)

        await event.message.answer(
            "✅ Ваш запрос успешно создан!\n"
            "С вами свяжутся в течение 24 часов.",
            attachments=[make_keyboard([
                [{"text": "🟢 Меню", "callback": "menu"}]
            ])]
        )
