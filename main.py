import asyncio
from dotenv import load_dotenv
from telegram.bot import telegram_bot
from data.database import init_db
from utils.helpers import logger

async def main():
    load_dotenv()
    await init_db()
    logger.info("PersonalAladdin starting...")
    await telegram_bot.run()

if __name__ == "__main__":
    asyncio.run(main())
