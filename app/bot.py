import logging
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from sheet import append_to_sheet
from parser import parse_input

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ALLOWED_IDS    = list(map(int, os.environ.get("ALLOWED_IDS", "").split(","))) if os.environ.get("ALLOWED_IDS") else []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Halo! Kirim data dengan format:\n\n"
        "• <code>rokok 31500</code> → tanggal hari ini\n"
        "• <code>25/03/2026 rokok 31500</code> → tanggal spesifik",
        parse_mode="HTML"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text    = update.message.text.strip()

    if ALLOWED_IDS and chat_id not in ALLOWED_IDS:
        await update.message.reply_text("⛔ Kamu tidak punya akses.")
        return

    parsed = parse_input(text)
    if not parsed:
        await update.message.reply_text(
            "❌ Format tidak dikenali.\n\nContoh:\n"
            "• <code>rokok 31500</code>\n"
            "• <code>25/03/2026 rokok 31500</code>",
            parse_mode="HTML"
        )
        return

    try:
        result = append_to_sheet(parsed["tanggal"], parsed["deskripsi"], parsed["nominal"])
        nominal_fmt = f"Rp {parsed['nominal']:,.0f}".replace(",", ".")
        await update.message.reply_text(
            f"✅ Tersimpan!\n\n"
            f"📅 <b>{parsed['tanggal']}</b>\n"
            f"📝 {parsed['deskripsi']}\n"
            f"💰 {nominal_fmt}\n\n"
            f"<i>{result}</i>",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error saving to sheet: {e}")
        await update.message.reply_text("❌ Gagal menyimpan ke sheet. Cek log bot.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    from telegram.error import NetworkError, TimedOut
    if isinstance(context.error, (NetworkError, TimedOut)):
        logger.debug(f"Network hiccup (auto-retry): {context.error}")
    else:
        logger.error(f"Unexpected error: {context.error}", exc_info=context.error)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started...")
    app.run_polling(drop_pending_updates=True)  # drop_pending_updates = anti loop!
    app.add_error_handler(error_handler)

if __name__ == "__main__":
    main()