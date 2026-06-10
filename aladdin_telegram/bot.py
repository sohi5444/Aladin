from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config.settings import settings
from core.risk_engine import risk_engine
from core.oms import oms
from core.real_macro import RealMacroBrain
from core.backtest_engine import run_backtest
from core.advanced_signals import generate_signal
from core.quant_engine import quant_engine
from core.backtest_advanced import walk_forward_backtest
import asyncio
import numpy as np

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
        self.app.add_handler(CommandHandler("quant", self.quant))
        self.app.add_handler(CommandHandler("optimize", self.optimize))
        self.app.add_handler(CommandHandler("simulate", self.simulate))
        self.app.add_handler(CommandHandler("correlation", self.correlation))
        self.app.add_handler(CommandHandler("full_backtest", self.full_backtest))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🟢 PersonalAladdin AI active. Commands: /signal, /quant, /optimize, /simulate, /correlation, /full_backtest, /macro, /risk")

    async def quant(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ticker = context.args[0].upper() if context.args else 'AAPL'
        signal, conf = quant_engine.ensemble_signal(ticker)
        tech = quant_engine.get_technical_indicators(ticker)
        macro = quant_engine.get_macro_factors()
        msg = (
            f"📊 *Quant Dashboard for {ticker}*\n"
            f"Ensemble Signal: {'BUY' if signal==1 else 'SELL' if signal==-1 else 'HOLD'} (conf: {conf:.0%})\n"
            f"RSI: {tech.get('rsi',0):.1f} | Volatility: {tech.get('volatility',0):.1f}%\n"
            f"MACD Hist: {tech.get('macd_hist',0):.2f} | ATR: {tech.get('atr',0):.2f}\n"
            f"GDP: {macro.get('gdp_growth',0):.1f}% | CPI: {macro.get('cpi_yoy',0):.1f}%\n"
            f"Fed Rate: {macro.get('fed_funds_rate',0):.2f}% | Unemp: {macro.get('unemployment',0):.1f}%"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def optimize(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Usage: /optimize AAPL,MSFT,GOOGL")
            return
        tickers = [t.upper() for t in args[0].split(',')]
        weights = quant_engine.optimize_portfolio(tickers)
        risk_parity = quant_engine.risk_parity(tickers)
        msg = "📈 *Portfolio Optimization*\nMax Sharpe:\n"
        for t,w in weights.items():
            msg += f"{t}: {w:.1%}\n"
        msg += "\nRisk Parity:\n"
        for t,w in risk_parity.items():
            msg += f"{t}: {w:.1%}\n"
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def simulate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ticker = context.args[0].upper() if context.args else 'AAPL'
        sim = quant_engine.monte_carlo(ticker)
        msg = (
            f"🔮 *Monte Carlo Simulation for {ticker} (252 days)*\n"
            f"Expected price: ${sim['expected_price']}\n"
            f"95% CI: ${sim['lower_95']} – ${sim['upper_95']}\n"
            f"Annualized volatility: {sim['volatility']}%"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def correlation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Usage: /correlation AAPL,MSFT,SPY")
            return
        tickers = [t.upper() for t in args[0].split(',')]
        data = yf.download(tickers, period='1y', progress=False)['Close']
        corr = data.corr().round(2)
        msg = "📉 *Correlation Matrix*\n```\n" + corr.to_string() + "\n```"
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def full_backtest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("Usage: /full_backtest AAPL 2020-01-01 2024-01-01")
            return
        ticker = args[0].upper()
        start = args[1]
        end = args[2]
        res = walk_forward_backtest(ticker, start, end)
        if res is None:
            await update.message.reply_text("Not enough data or backtest failed.")
            return
        msg = (
            f"📊 *Walk‑Forward Backtest {ticker}*\n"
            f"Period: {start} to {end}\n"
            f"Total Return: {res['total_return_pct']}%\n"
            f"Sharpe Ratio: {res['sharpe']}\n"
            f"Max Drawdown: {res['max_dd_pct']}%\n"
            f"Win Rate: {res['win_rate_pct']}%\n"
            f"Trades: {res['num_trades']}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

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
                f"Regime: {regime}\nGDP Growth: {gdp}%\nCPI YoY: {cpi}%\n"
                f"Unemployment: {unemp}%\nFed Funds Rate: {fed}%"
            )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def risk(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        var = await risk_engine.take_snapshot()
        await update.message.reply_text(f"📉 VaR (95%): {var}%")

    async def trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("Usage: /trade buy 100 AAPL")
            return
        side = args[0].lower()
        qty = float(args[1])
        ticker = args[2].upper()
        order_ref = await oms.create_order(ticker, side, qty)
        await update.message.reply_text(f"Paper order {order_ref} created")

    async def backtest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("Usage: /backtest AAPL 2022-01-01 2024-01-01")
            return
        ticker = args[0].upper()
        start = args[1]
        end = args[2]
        res = run_backtest(ticker, start, end)
        if res:
            msg = f"📊 *Backtest {ticker}*\nReturn: {res['return_pct']}%\nSharpe: {res['sharpe']}\nMax DD: {res['max_dd_pct']}%\nWin Rate: {res['win_rate']}%"
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("Backtest failed.")

    async def briefing(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        regime = RealMacroBrain.get_regime()
        await update.message.reply_text(f"🧠 *AI Briefing*\nCurrent regime: {regime}\nMonitor /signal for trades.", parse_mode="Markdown")

    async def signal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ticker = context.args[0].upper() if context.args else 'AAPL'
        sig = generate_signal(ticker)
        msg = (
            f"📡 *Aladdin Signal for {ticker}*\n"
            f"Action: {sig['action']}\nConfidence: {sig['confidence']}\n"
            f"Regime: {sig['factors']['regime']}\nStress Loss: ${sig['stress_loss']}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def run(self):
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        await asyncio.Event().wait()

telegram_bot = TelegramBot()
