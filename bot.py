from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from config import TOKEN, ADMIN_ID
from keep_alive import keep_alive
import re, time

users = {}
queue = []
liked = {}

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    keyboard = [
        [KeyboardButton("🔗 Добавить видео")],
        [KeyboardButton("📋 Получить задания"), KeyboardButton("✅ Подтвердить лайки")],
        [KeyboardButton("📊 Топ участников"), KeyboardButton("📜 Правила")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text="👋 Добро пожаловать!\nИспользуй кнопки ниже 👇", reply_markup=reply_markup)
    users[user.id] = {"videos": [], "likes_given": [], "likes_received": 0}

def is_tiktok_link(text):
    return "tiktok.com" in text

def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text

    if text == "📜 Правила":
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="📋 <b>Правила:</b>\n\n1. Добавляй только TikTok-ссылки\n2. Лайкай 3 видео — получай лайки на своё\n3. Подтверждай только после просмотра 20 секунд\n4. Не жульничай 😉",
            parse_mode="HTML"
        )
    elif text == "🔗 Добавить видео":
        context.bot.send_message(chat_id=update.effective_chat.id, text="🔗 Отправь ссылку на своё видео с TikTok")
    elif is_tiktok_link(text):
        if text in [v for _, v in queue]:
            context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Это видео уже в очереди.")
            return
        if user_id not in users:
            users[user_id] = {"videos": [], "likes_given": [], "likes_received": 0}
        users[user_id]["videos"].append(text)
        context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Видео добавлено в очередь!")
    elif text == "📋 Получить задания":
        tasks = []
        for uid, link in queue:
            if uid == user_id or link in users.get(user_id, {}).get("likes_given", []):
                continue
            tasks.append(link)
            if len(tasks) == 3:
                break
        if not tasks:
            context.bot.send_message(chat_id=update.effective_chat.id, text="📭 Нет заданий сейчас. Попробуй позже.")
        else:
            if user_id not in users:
                users[user_id] = {"videos": [], "likes_given": [], "likes_received": 0}
            users[user_id]["current_tasks"] = tasks
            users[user_id]["task_time"] = time.time()
            msg = "\n".join([f"🔗 {t}" for t in tasks])
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"👍 Лайкни эти видео:\n{msg}\n\n⏳ Через 20 сек. нажми '✅ Подтвердить лайки'")
    elif text == "✅ Подтвердить лайки":
        now = time.time()
        if user_id not in users or "task_time" not in users[user_id] or now - users[user_id]["task_time"] < 20:
            context.bot.send_message(chat_id=update.effective_chat.id, text="⏱ Подтверждение доступно только через 20 секунд после получения заданий.")
            return
        for link in users[user_id]["current_tasks"]:
            users[user_id]["likes_given"].append(link)
        if user_id in users and users[user_id]["videos"]:
            queue.append((user_id, users[user_id]["videos"][-1]))
        context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Спасибо! Твоё видео получит лайки.")
    elif text == "📊 Топ участников":
        top = sorted(users.items(), key=lambda x: len(x[1].get('likes_given', [])), reverse=True)
        msg = "🏆 <b>Топ участников:</b>\n\n"
        for i, (uid, data) in enumerate(top[:5], start=1):
            msg += f"{i}. ID {uid} — 👍 {len(data['likes_given'])} лайков\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="HTML")
    elif text == "/admin" and user_id == ADMIN_ID:
        if not queue:
            context.bot.send_message(chat_id=update.effective_chat.id, text="🧹 Очередь пуста")
        else:
            msg = "\n".join([f"{i+1}. {l}" for i, (uid, l) in enumerate(queue)])
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"📝 Очередь:\n{msg}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="❓ Неизвестная команда.")

def main():
    keep_alive()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", handle_message))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()/a
