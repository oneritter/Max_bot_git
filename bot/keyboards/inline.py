from maxapi.types import (
    InlineKeyboardAttachment,
    CallbackButton,
    LinkButton,
    RequestContactButton,
)


def make_keyboard(buttons: list[list[dict]]) -> InlineKeyboardAttachment:
    """Build inline keyboard from a 2D list of button dicts.

    Each button dict:
        {"text": "Label", "callback": "slug"}          — callback button
        {"text": "Label", "url": "https://..."}         — link button
        {"text": "Label", "request_contact": True}      — contact request
    """
    rows = []
    for row in buttons:
        row_buttons = []
        for btn in row:
            if "callback" in btn:
                row_buttons.append(CallbackButton(text=btn["text"], payload=btn["callback"]))
            elif "url" in btn:
                row_buttons.append(LinkButton(text=btn["text"], url=btn["url"]))
            elif "request_contact" in btn:
                row_buttons.append(RequestContactButton(text=btn["text"]))
            else:
                row_buttons.append(CallbackButton(text=btn["text"], payload=btn.get("payload", "noop")))
        rows.append(row_buttons)
    return InlineKeyboardAttachment(payload=rows)


def main_menu_keyboard() -> InlineKeyboardAttachment:
    return make_keyboard([
        [{"text": "👨 Работа с партнёрами", "callback": "partners"}],
        [{"text": "🧩 Наши технологии", "callback": "technology"}],
        [{"text": "📘 Памятки и инструкции", "callback": "pamyatki"}],
        [{"text": "🔌 Подключение онлайн ТТ", "callback": "online_tt"}],
        [{"text": "🎓 Обучение ТМ / операторов", "callback": "education"}],
        [{"text": "📣 Рекламные материалы", "callback": "ads"}],
        [{"text": "❓ Нет нужной информации", "callback": "no_info"}],
        [{"text": "💡 Предложить идею", "callback": "idea"}],
    ])


def back_and_menu(back_callback: str | None = None) -> list[list[dict]]:
    """Standard back + menu row."""
    row = []
    if back_callback:
        row.append({"text": "⬅️ Назад", "callback": back_callback})
    row.append({"text": "🟢 Меню", "callback": "menu"})
    return [row]


def category_keyboard(items: list[dict], back_callback: str | None = None) -> InlineKeyboardAttachment:
    """Build keyboard from category items + back/menu row.

    items: [{"text": "Name", "callback": "slug"}, ...]
    """
    buttons = [[item] for item in items]
    buttons.extend(back_and_menu(back_callback))
    return make_keyboard(buttons)
