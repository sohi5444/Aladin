import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))
    DATABASE_URL = "sqlite+aiosqlite:///./data_db/aladdin.db"
settings = Settings()
