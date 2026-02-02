import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from agent import chat
from reminders import reminder_loop

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    print(f"User started: {user_id}")
    await update.message.reply_text("Hey! I'm your assistant. I'll remember things and remind you when needed.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    user_message = update.message.text
    print(f"Message from {user_id}: {user_message}")
    response = await chat(user_id, user_message)
    await update.message.reply_text(response)

async def send_reminder(app: Application, user_id: str, reminder: dict):
    print(f"Sending reminder to {user_id}: {reminder['text']}")
    try:
        await app.bot.send_message(chat_id=int(user_id), text=f"🔔 REMINDER: {reminder['text']}")
    except Exception as e:
        print(f"Failed to send reminder to {user_id}: {e}")

async def post_init(app: Application):
    async def reminder_callback(user_id: str, reminder: dict):
        await send_reminder(app, user_id, reminder)
    asyncio.create_task(reminder_loop(reminder_callback, interval=60))

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
