import os
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ["BOT_TOKEN"]

conn = sqlite3.connect("content.db", check_same_thread=False)
cursor = conn.cursor()

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()

    cursor.execute(
        "SELECT link FROM content WHERE text LIKE ? LIMIT 5",
        (f"%{query}%",)
    )

    results = cursor.fetchall()

    if not results:
        await update.message.reply_text("❌ لا توجد نتائج")
        return

    reply = "🔎 نتائج البحث:\n\n"
    for r in results:
        reply += f"• {r[0]}\n"

    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))

print("🤖 Bot is running...")
app.run_polling()
