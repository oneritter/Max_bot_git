from maxapi import Router
from maxapi.types import MessageCreated, MessageCallback, Command

from keyboards.inline import make_keyboard
from states.forms import RequestState

router = Router()

_request_states: dict[str, dict] = {}


@router.message_created(Command("request"))
async def cmd_request(event: MessageCreated):
    await event.message.answer(
        "🔐 Допы по заявке\n\nДля продолжения пройдите авторизацию:",
        attachments=[make_keyboard([
            [{"text": "🔑 Авторизация", "callback": "request_auth"}]
        ])]
    )


@router.message_callback()
async def cb_request_auth(event: MessageCallback):
    if event.callback.payload != "request_auth":
        return
    await event.callback.answer("")

    uid = str(event.callback.user.user_id)
    _request_states[uid] = {"state": RequestState.WAITING_ORDER_NUMBER}

    await event.bot.send_message(
        chat_id=event.chat_id,
        text=(
            "✅ Авторизация прошла успешно!\n\n"
            "Введите номер заявки:"
        ),
        attachments=[make_keyboard([
            [{"text": "📋 Допы по заявке", "callback": "request_input"}]
        ])]
    )


@router.message_callback()
async def cb_request_input(event: MessageCallback):
    if event.callback.payload != "request_input":
        return
    await event.callback.answer("")

    uid = str(event.callback.user.user_id)
    _request_states[uid] = {"state": RequestState.WAITING_ORDER_NUMBER}
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="Введите номер заявки:"
    )


@router.message_created()
async def handle_order_number(event: MessageCreated):
    uid = str(event.message.sender.user_id)
    state_data = _request_states.get(uid)
    if not state_data or state_data.get("state") != RequestState.WAITING_ORDER_NUMBER:
        return

    text = (event.message.body or {}).get("text", "").strip()
    if not text:
        return

    _request_states.pop(uid, None)

    # STUB: hardcoded response as in the original Telegram bot
    await event.message.answer(
        f"📋 Допы по заявке №{text}\n\n"
        "🏪 Партнёр: iShop72\n"
        "📝 Заявка: №277470920\n\n"
        "Допы:\n"
        "• ОТП банк — одобрено\n"
        "• МТС банк — на рассмотрении\n\n"
        "⚠️ Данные тестовые (заглушка). Реальная интеграция будет добавлена позднее.",
        attachments=[make_keyboard([
            [{"text": "🟢 Меню", "callback": "menu"}]
        ])]
    )
