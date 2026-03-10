import os
from maxapi import Router
from maxapi.types import MessageCallback

from db.database import SessionLocal
from db.crud import (
    get_user_by_max_id,
    get_category_by_slug,
    get_children_categories,
    get_documents_by_category,
    get_links_by_category,
    update_document_file_id,
)
from keyboards.inline import category_keyboard, make_keyboard, back_and_menu
from config import UPLOAD_DIR

router = Router()

# Known top-level slugs that map to menu buttons
TOP_LEVEL_SLUGS = {"partners", "technology", "pamyatki", "online_tt", "ads"}


@router.message_callback()
async def handle_category_callback(event: MessageCallback):
    slug = event.callback.payload
    if not slug or slug in ("menu", "noop"):
        return

    user_id = str(event.callback.user.user_id)

    db = SessionLocal()
    try:
        user = get_user_by_max_id(db, user_id)
        if not user or user.status != "approved":
            await event.callback.answer("Доступ не предоставлен.")
            return

        category = get_category_by_slug(db, slug)
        if category is None:
            return  # Not a category callback, skip

        await event.callback.answer("")

        # Determine back target
        if category.parent_id:
            parent = db.query(
                __import__("db.models", fromlist=["Category"]).Category
            ).filter_by(id=category.parent_id).first()
            back_target = parent.slug if parent else "menu"
        else:
            back_target = "menu"

        # Get children
        children = get_children_categories(db, category.id)

        # Get documents
        documents = get_documents_by_category(db, category.id)

        # Get external links
        links = get_links_by_category(db, category.id)

        # Build response
        if children:
            # Show subcategories as buttons
            items = [{"text": f"{c.icon or ''} {c.name}".strip(), "callback": c.slug} for c in children]
            kb = category_keyboard(items, back_callback=back_target)
            await event.bot.send_message(
                chat_id=event.chat_id,
                text=f"📂 {category.name}",
                attachments=[kb]
            )

        # Send documents
        for doc in documents:
            file_path = os.path.join(UPLOAD_DIR, doc.file_path)
            if not os.path.exists(file_path):
                await event.bot.send_message(
                    chat_id=event.chat_id,
                    text=f"📄 {doc.title} (файл не найден)"
                )
                continue

            # Send file via upload
            with open(file_path, "rb") as f:
                upload_result = await event.bot.upload_file(
                    file=f,
                    chat_id=event.chat_id
                )
                if upload_result:
                    await event.bot.send_message(
                        chat_id=event.chat_id,
                        text=f"📄 {doc.title}",
                        attachments=[upload_result]
                    )

        # Send external links
        if links:
            link_buttons = [[{"text": link.title, "url": link.url}] for link in links]
            link_buttons.extend(back_and_menu(back_target))
            await event.bot.send_message(
                chat_id=event.chat_id,
                text="🔗 Ссылки:",
                attachments=[make_keyboard(link_buttons)]
            )

        # If only documents (no children, no links), add back/menu
        if documents and not children and not links:
            await event.bot.send_message(
                chat_id=event.chat_id,
                text="—",
                attachments=[make_keyboard(back_and_menu(back_target))]
            )

    finally:
        db.close()
