import asyncio
import os
import threading
from dotenv import load_dotenv
from aladdin_telegram.bot import telegram_bot
from data.database import init_db
from utils.helpers import logger

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

async def health(request):
    return JSONResponse({"status": "alive"})

app = Starlette(routes=[Route("/health", health)])

async def main():
    load_dotenv()
    await init_db()
    logger.info("PersonalAladdin starting...")
    await telegram_bot.run()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=port), daemon=True).start()
    asyncio.run(main())
