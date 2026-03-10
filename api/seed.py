"""Seed script: populates initial category tree matching the Finbox bot structure."""
from database import init_db, SessionLocal
from models import Category

SEED_CATEGORIES = [
    # Root menu items
    {"name": "Работа с партнёрами", "slug": "partners", "icon": "👨", "sort_order": 1, "children": [
        {"name": "Презентации", "slug": "partners_presentations", "sort_order": 1},
        {"name": "Оферта Неотех", "slug": "partners_oferta_neotech", "sort_order": 2},
        {"name": "Оферта УФТ", "slug": "partners_oferta_uft", "sort_order": 3},
        {"name": "Карточка Неотех", "slug": "partners_card_neotech", "sort_order": 4},
        {"name": "Карточка УФТ", "slug": "partners_card_uft", "sort_order": 5},
        {"name": "Процесс формирования ссылки ЛПР", "slug": "partners_lpr_link", "sort_order": 6},
    ]},
    {"name": "Наши технологии", "slug": "technology", "icon": "🧩", "sort_order": 2, "children": [
        {"name": "Метод", "slug": "tech_method", "sort_order": 1},
        {"name": "Плайт", "slug": "tech_plait", "sort_order": 2},
        {"name": "УФТ / ОФП", "slug": "tech_uft_ofp", "sort_order": 3},
        {"name": "Кэш брокер", "slug": "tech_cash_broker", "sort_order": 4},
        {"name": "ЕМП (МПМК)", "slug": "tech_emp", "sort_order": 5},
    ]},
    {"name": "Памятки и инструкции", "slug": "pamyatki", "icon": "📘", "sort_order": 3, "children": [
        {"name": "Оплата кредита", "slug": "pam_oplata", "sort_order": 1, "children": [
            {"name": "Альфа банк", "slug": "pam_oplata_alfa", "sort_order": 1},
            {"name": "А-Деньги", "slug": "pam_oplata_adengi", "sort_order": 2},
            {"name": "БРС", "slug": "pam_oplata_brs", "sort_order": 3},
            {"name": "Denum", "slug": "pam_oplata_denum", "sort_order": 4},
            {"name": "Деньга", "slug": "pam_oplata_denga", "sort_order": 5},
            {"name": "Дополучкино", "slug": "pam_oplata_dopoluchkino", "sort_order": 6},
            {"name": "Кредит Европа Банк", "slug": "pam_oplata_keb", "sort_order": 7},
            {"name": "Лайм-Займ", "slug": "pam_oplata_lime", "sort_order": 8},
            {"name": "Локо банк", "slug": "pam_oplata_loko", "sort_order": 9},
            {"name": "Миг кредит", "slug": "pam_oplata_mig", "sort_order": 10},
            {"name": "МТС банк", "slug": "pam_oplata_mts", "sort_order": 11},
            {"name": "ОТП банк", "slug": "pam_oplata_otp", "sort_order": 12},
            {"name": "Плайт", "slug": "pam_oplata_plait", "sort_order": 13},
            {"name": "Paylate", "slug": "pam_oplata_paylate", "sort_order": 14},
            {"name": "Ренесанс банк", "slug": "pam_oplata_renaissance", "sort_order": 15},
            {"name": "Совком банк", "slug": "pam_oplata_sovkom", "sort_order": 16},
            {"name": "Совком Экспресс", "slug": "pam_oplata_sovkom_express", "sort_order": 17},
            {"name": "Т-банк", "slug": "pam_oplata_tbank", "sort_order": 18},
            {"name": "Уралсиб банк", "slug": "pam_oplata_uralsib", "sort_order": 19},
            {"name": "Фрилли и Веббанкир", "slug": "pam_oplata_frilly", "sort_order": 20},
            {"name": "Хоум экспресс", "slug": "pam_oplata_home", "sort_order": 21},
        ]},
        {"name": "Подписание КД", "slug": "pam_kd", "sort_order": 2, "children": [
            {"name": "Альфа-Банк POS+КАРТА", "slug": "pam_kd_alfa", "sort_order": 1},
            {"name": "БРС", "slug": "pam_kd_brs", "sort_order": 2},
            {"name": "Деньга", "slug": "pam_kd_denga", "sort_order": 3},
            {"name": "Кредит Европа Банк", "slug": "pam_kd_keb", "sort_order": 4},
            {"name": "Локо банк", "slug": "pam_kd_loko", "sort_order": 5},
            {"name": "Миг кредит", "slug": "pam_kd_mig", "sort_order": 6},
            {"name": "МТС банк", "slug": "pam_kd_mts", "sort_order": 7},
            {"name": "ОТП банк", "slug": "pam_kd_otp", "sort_order": 8},
            {"name": "Ренесанс банк", "slug": "pam_kd_renaissance", "sort_order": 9},
            {"name": "Совком банк", "slug": "pam_kd_sovkom", "sort_order": 10},
            {"name": "Совком Экспресс", "slug": "pam_kd_sovkom_express", "sort_order": 11},
            {"name": "Т-банк", "slug": "pam_kd_tbank", "sort_order": 12},
            {"name": "Уралсиб", "slug": "pam_kd_uralsib", "sort_order": 13},
            {"name": "Фрилли", "slug": "pam_kd_frilly", "sort_order": 14},
        ]},
        {"name": "Требования для клиентов", "slug": "pam_requirements", "sort_order": 3},
        {"name": "Сводная информация по банкам", "slug": "pam_summary", "sort_order": 4},
        {"name": "Запрещённые территории", "slug": "pam_forbidden", "sort_order": 5},
        {"name": "Инструкция по работе с ПО", "slug": "pam_instructions", "sort_order": 6, "children": [
            {"name": "Инструкции PDF", "slug": "pam_instr_pdf", "sort_order": 1, "children": [
                {"name": "Заведение КЗ в ПО Finbox", "slug": "pam_instr_kz", "sort_order": 1},
                {"name": "Инструкция по большим чекам", "slug": "pam_instr_big_checks", "sort_order": 2},
                {"name": "Инструкции по работе через КЦ и WhatsApp", "slug": "pam_instr_kc_whatsapp", "sort_order": 3},
                {"name": "Инструкции по оформлению заявки", "slug": "pam_instr_application", "sort_order": 4},
                {"name": "Копирование заявки в ПО Finbox", "slug": "pam_instr_copy", "sort_order": 5},
                {"name": "Отмена КД при отказе клиента", "slug": "pam_instr_cancel", "sort_order": 6},
                {"name": "Презентации по кредитным картам", "slug": "pam_instr_cc_presentations", "sort_order": 7},
            ]},
            {"name": "Видеоинструкции", "slug": "pam_video", "sort_order": 2, "children": [
                {"name": "Оформление заявки — новый интерфейс Госуслуги", "slug": "pam_video_gosuslugi", "sort_order": 1},
                {"name": "Оформление заявки — новый интерфейс вручную", "slug": "pam_video_manual", "sort_order": 2},
                {"name": "Оформление короткой заявки — старый интерфейс", "slug": "pam_video_short", "sort_order": 3},
                {"name": "Заведение кредитной заявки в Finbox", "slug": "pam_video_finbox", "sort_order": 4},
            ]},
        ]},
        {"name": "Вывод АВ", "slug": "pam_av", "sort_order": 7, "children": [
            {"name": "Вывод АВ — основной", "slug": "pam_av_main", "sort_order": 1},
            {"name": "Мой налог", "slug": "pam_av_tax", "sort_order": 2},
            {"name": "Наймикс", "slug": "pam_av_naimix", "sort_order": 3},
            {"name": "Связка", "slug": "pam_av_svyazka", "sort_order": 4},
            {"name": "Переподписание", "slug": "pam_av_resign", "sort_order": 5},
        ]},
        {"name": "Кредитные карты", "slug": "pam_cc", "sort_order": 8, "children": [
            {"name": "Альфа банк карты", "slug": "pam_cc_alfa", "sort_order": 1},
            {"name": "ВТБ карты", "slug": "pam_cc_vtb", "sort_order": 2},
            {"name": "Карта Халва", "slug": "pam_cc_halva", "sort_order": 3},
        ]},
    ]},
    {"name": "Подключение онлайн ТТ", "slug": "online_tt", "icon": "🔌", "sort_order": 4, "children": [
        {"name": "Видео-инструкции", "slug": "tt_video", "sort_order": 1, "children": [
            {"name": "Инструкция ИМ/ДТ", "slug": "tt_video_imdt", "sort_order": 1},
            {"name": "Инструкция ОФП", "slug": "tt_video_ofp", "sort_order": 2},
            {"name": "Страховка", "slug": "tt_video_insurance", "sort_order": 3},
        ]},
        {"name": "Инструкции и памятки", "slug": "tt_instructions", "sort_order": 2, "children": [
            {"name": "ОФП онлайн", "slug": "tt_instr_ofp", "sort_order": 1},
            {"name": "Анализ сайта", "slug": "tt_instr_analysis", "sort_order": 2},
            {"name": "Подбор интеграции", "slug": "tt_instr_integration", "sort_order": 3},
        ]},
        {"name": "Интеграция и подключение", "slug": "tt_integration", "sort_order": 3, "children": [
            {"name": "Точки входа", "slug": "tt_int_entry", "sort_order": 1},
            {"name": "Сравнение технологий", "slug": "tt_int_compare", "sort_order": 2},
            {"name": "Оформление через WhatsApp", "slug": "tt_int_whatsapp", "sort_order": 3},
            {"name": "Презентация онлайн партнёра", "slug": "tt_int_partner_pres", "sort_order": 4},
            {"name": "Создание запроса на подключение", "slug": "tt_int_request", "sort_order": 5},
            {"name": "Элементы интеграции на сайт", "slug": "tt_int_elements", "sort_order": 6},
        ]},
        {"name": "Чек-листы", "slug": "tt_checklists", "sort_order": 4, "children": [
            {"name": "Чек-лист ИМ/ДТ", "slug": "tt_check_imdt", "sort_order": 1},
            {"name": "Чек-лист ТМ по онлайн", "slug": "tt_check_tm", "sort_order": 2},
        ]},
        {"name": "Обратная связь", "slug": "tt_feedback", "sort_order": 5},
    ]},
    {"name": "Рекламные материалы", "slug": "ads", "icon": "📣", "sort_order": 6, "children": [
        {"name": "А4", "slug": "ads_a4", "sort_order": 1},
        {"name": "Домик", "slug": "ads_domik", "sort_order": 2},
        {"name": "Кэш", "slug": "ads_cash", "sort_order": 3},
        {"name": "Стикер", "slug": "ads_sticker", "sort_order": 4},
    ]},
]


def _insert_tree(db, categories, parent_id=None):
    for cat_data in categories:
        children = cat_data.pop("children", [])
        cat = Category(parent_id=parent_id, **cat_data)
        db.add(cat)
        db.flush()  # get cat.id
        if children:
            _insert_tree(db, children, parent_id=cat.id)


def seed():
    init_db()
    db = SessionLocal()
    try:
        existing = db.query(Category).count()
        if existing > 0:
            print(f"Database already has {existing} categories. Skipping seed.")
            return

        _insert_tree(db, SEED_CATEGORIES)
        db.commit()
        total = db.query(Category).count()
        print(f"Seeded {total} categories successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
