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
MEMBER_IDS     = list(map(int, os.environ.get("MEMBER_IDS", "").split(",")))  if os.environ.get("MEMBER_IDS")  else []
ALL_ALLOWED    = ALLOWED_IDS + MEMBER_IDS

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

    # Cek whitelist
    if ALL_ALLOWED and chat_id not in ALL_ALLOWED:
        await update.message.reply_text("⛔ Kamu tidak punya akses.")
        return

    # Parse input
    parsed = parse_input(text)
    if not parsed:
        await update.message.reply_text(
            "❌ Format tidak dikenali.\n\nContoh:\n"
            "• <code>rokok 31500</code>\n"
            "• <code>25/03/2026 rokok 31500</code>",
            parse_mode="HTML"
        )
        return

    # Simpan ke sheet
    try:
        result = append_to_sheet(parsed["tanggal"], parsed["deskripsi"], parsed["nominal"], chat_id)
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

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started...")
    app.run_polling(drop_pending_updates=True)  # drop_pending_updates = anti loop!

if __name__ == "__main__":
    main()