import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
import asyncio

API_TOKEN = "8500985562:AAFORdXvn9vP6I5J1G2TApsZ3Qh7JYELraI"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ===== قاعدة البيانات =====
import re

def normalize(text: str):
    text = text.lower()
    text = re.sub(r"[ًٌٍَُِّْ]", "", text)  # إزالة التشكيل
    text = text.replace("ة", "ه")
    text = re.sub(r"\bال", "", text)        # إزالة (ال)
    return text

FIQH_SYNONYMS = {
    "قصر": ["قصر", "مسافر", "سفر", "جمع"],
    "صلاة": ["صلاة", "يصلي", "الصلاه"],
    "صيام": ["صيام", "صائم", "صوم", "رمضان"],
    "اكل": ["اكل", "أكل", "فطر"],
    "نسي": ["نسي", "ناسيا", "ناسياً", "نسيان"],
    "حج": ["حج", "الحج", "الحجاج", "مناسك"],
}

def extract_keywords(query: str):
    words = normalize(query).split()
    expanded = set(words)

    for w in words:
        for key, values in FIQH_SYNONYMS.items():
            if w in values:
                expanded.update(values)

    return list(expanded)

def search_db(query: str):
    conn = sqlite3.connect("content.db")
    cursor = conn.cursor()

    keywords = extract_keywords(query)
    conditions = []
    params = []

    for k in keywords:
        conditions.append("text LIKE ?")
        params.append(f"%{k}%")

    sql = "SELECT text, link FROM content WHERE " + " OR ".join(conditions) + " LIMIT 5"

    cursor.execute(sql, params)
    results = cursor.fetchall()
    conn.close()
    return results


# ===== /start =====
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🔍 أهلاً بك\n\n"
        "اكتب أي كلمة للبحث داخل مقاطع القناة.\n"
        "مثال:\n"
        "حج\n"
        "صلاة\n"
        "توحيد"
    )

# ===== البحث =====
@dp.message()
async def search(message: Message):
    keyword = message.text.strip()
    results = search_db(keyword)

    if not results:
        await message.answer("❌ لا توجد نتائج")
        return

    reply = "🔎 نتائج البحث:\n\n"
    for i, (_, link) in enumerate(results, 1):
        reply += f"{i}- {link}\n"

    await message.answer(reply)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
