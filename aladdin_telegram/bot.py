from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config.settings import settings
from core.risk_engine import risk_engine
from core.oms import oms
from core.real_macro import RealMacroBrain
from core.backtest_engine import run_backtest
from core.advanced_signals import generate_signal
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
        self.app.add_handler(CommandHandler("backtest", self.backtest))
        self.app.add_handler(CommandHandler("briefing", self.briefing))
        self.app.add_handler(CommandHandler("signal", self.signal))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🟢 PersonalAladdin active.\nCommands:\n/risk\n/macro\n/trade buy qty TICKER\n/backtest TICKER START END\n/briefing\n/signal TICKER"
        )

    async def risk(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        var = await risk_engine.take_snapshot()
        await update.message.reply_text(f"📉 VaR (95%): {var}%")

    async def macro(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        regime = RealMacroBrain.get_regime()
        gdp = RealMacroBrain.get_gdp()
        cpi = RealMacroBrain.get_cpi_yoy()
        unemp = RealMacroBrain.get_unemployment()
        fed = RealMacroBrain.get_fed_rate()
        if gdp is None:
            msg = "⚠️ FRED API key missing or no data. Set FRED_API_KEY in Render env."
        else:
            msg = (
                f"🌍 *Real Macro Data*\n"
                f"Regime: {regime}\n"
                f"GDP Growth: {gdp}%\n"
                f"CPI YoY: {cpi}%\n"
                f"Unemployment: {unemp}%\n"
                f"Fed Funds Rate: {fed}%"
            )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("Usage: /trade buy 100 AAPL")
            return
        side = args[0].lower()
        qty = float(args[1])
        ticker = args[2].upper()
        order_ref = await oms.create_order(ticker, side, qty)
        await update.message.reply_text(f"Paper order {order_ref} created for {side.upper()} {qty} {ticker}")

    async def backtest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("Usage: /backtest AAPL 2022-01-01 2024-01-01")
            return
        ticker = args[0].upper()
        start = args[1]
        end = args[2]
        res = run_backtest(ticker, start, end)
        if res is None:
            await update.message.reply_text("Failed to fetch data or run backtest.")
            return
        msg = (
            f"📊 *Backtest {ticker}*\n"
            f"Period: {res['start']} to {res['end']}\n"
            f"Return: {res['return_pct']:.2f}%\n"
            f"Max Drawdown: {res['max_dd_pct']:.2f}%\n"
            f"Sharpe Ratio: {res['sharpe']:.2f}\n"
            f"Win Rate: {res['win_rate']:.1f}%\n"
            f"Trades: {res['trades']}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def briefing(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        regime = RealMacroBrain.get_regime()
        await update.message.reply_text(f"🧠 *AI Briefing*\nCurrent regime: {regime}\nNo actionable events. Monitor macro data.", parse_mode="Markdown")

    async def signal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        ticker = args[0].upper() if args else 'AAPL'
        sig = generate_signal(ticker)
        msg = (
            f"📡 *Aladdin‑Style Signal for {ticker}*\n"
            f"Action: {sig['action']}\n"
            f"Confidence: {sig['confidence']}\n"
            f"Score: {sig['score']}\n"
            f"Regime: {sig['factors']['regime']}\n"
            f"Stress Loss (COVID scenario): ${sig['stress_loss']}\n"
            f"Technical crossover: {sig['technicals'].get('crossover_signal', 0)}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def run(self):
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        await asyncio.Event().wait()

telegram_bot = TelegramBot()
