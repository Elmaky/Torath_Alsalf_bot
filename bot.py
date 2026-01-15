import os
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

BOT_TOKEN = os.environ["BOT_TOKEN"]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler()
async def search_handler(message: types.Message):
    query = message.text.strip()

    if len(query) < 2:
        await message.reply("❌ اكتب كلمة أو جملة للبحث")
        return

    conn = sqlite3.connect("content.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT text, link FROM content WHERE text LIKE ? LIMIT 10",
        (f"%{query}%",)
    )
    results = cursor.fetchall()
    conn.close()

    if not results:
        await message.reply("❌ لا توجد نتائج")
        return

    reply = "🔍 **نتائج البحث:**\n\n"
    for i, (text, link) in enumerate(results, 1):
        short = text[:100].replace("\n", " ")
        reply += f"{i}- {short}...\n🔗 {link}\n\n"

    await message.reply(reply, disable_web_page_preview=True)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
