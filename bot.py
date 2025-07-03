import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

import asyncio

TOKEN = "ТВОЙ_ТОКЕН_ТУТ"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🔗 Добавить видео")],
        [KeyboardButton("📋 Получить задания"), KeyboardButton("✅ Подтвердить лайки")],
        [KeyboardButton("📊 Топ участников"), KeyboardButton("📜 Правила")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 Добро пожаловать!\nИспользуй кнопки ниже 👇", reply_markup=reply_markup)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"Ты написал: {text}")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Бот запущен...")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
