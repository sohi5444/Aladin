from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config.settings import settings
from core.risk_engine import risk_engine
from core.macro_brain import macro
from core.ai_layer import ai
from core.oms import oms
import asyncio

class TelegramBot:
    def __init__(self):
        self.app = Application.builder().token(settings.TELEGRAM_TOKEN).build()
        self.register_handlers()

    def register_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("risk", self.risk))
        self.app.add_handler(CommandHandler("macro", self.macro))
        self.app.add_handler(CommandHandler("trade", self.trade))
        self.app.add_handler(CommandHandler("briefing", self.briefing))

    async def start(self, update, context):
        await update.message.reply_text("PersonalAladdin active. Commands: /risk, /macro, /trade, /briefing")

    async def risk(self, update, context):
        snap = await risk_engine.take_snapshot()
        await update.message.reply_text(f"VaR 95%: {snap.var_95}%")

    async def macro(self, update, context):
        dash = await macro.get_dashboard()
        await update.message.reply_text(f"Regime: {dash['regime']}\nSurprise: {dash['surprise_index']}")

    async def trade(self, update, context):
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("Usage: /trade buy 100 AAPL")
            return
        ref = await oms.create_order(args[2], args[0], float(args[1]))
        await update.message.reply_text(f"Order {ref} created")

    async def briefing(self, update, context):
        macro_dash = await macro.get_dashboard()
        risk_snap = await risk_engine.take_snapshot()
        brief = await ai.generate_daily_briefing(macro_dash, risk_snap, "Portfolio: $10k")
        await update.message.reply_text(brief)

    async def run(self):
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        await asyncio.Event().wait()

telegram_bot = TelegramBot()
