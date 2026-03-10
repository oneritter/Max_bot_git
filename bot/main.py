import asyncio
import logging

from maxapi import Bot, Dispatcher
from config import MAX_BOT_TOKEN
from db.database import init_db
from handlers import register_all_handlers

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def main():
    logger.info("Initializing database...")
    init_db()

    logger.info("Starting bot...")
    bot = Bot(MAX_BOT_TOKEN)
    dp = Dispatcher()

    register_all_handlers(dp)

    logger.info("Bot is running (polling mode)")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
