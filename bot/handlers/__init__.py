from maxapi import Dispatcher

from handlers.auth import router as auth_router
from handlers.menu import router as menu_router
from handlers.content import router as content_router
from handlers.education import router as education_router
from handlers.feedback import router as feedback_router
from handlers.request import router as request_router


def register_all_handlers(dp: Dispatcher):
    dp.include_routers(
        auth_router,
        menu_router,
        content_router,
        education_router,
        feedback_router,
        request_router,
    )
