from telethon import TelegramClient
import sqlite3
import asyncio

# ====== بياناتك ======
API_ID = 35154140
API_HASH = "017e4aff6a90364fac02b097250e5dff"
CHANNEL_USERNAME = "meknaz_alalbany"
BATCH_LIMIT = 3000   # كل دفعة
SLEEP_TIME = 1

# ====== قاعدة البيانات ======
conn = sqlite3.connect("content.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    link TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")
conn.commit()

def get_last_id():
    cursor.execute("SELECT value FROM meta WHERE key='last_id'")
    row = cursor.fetchone()
    return int(row[0]) if row else 0

def save_last_id(mid):
    cursor.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES ('last_id', ?)",
        (str(mid),)
    )
    conn.commit()

# ====== Telethon ======
client = TelegramClient("session", API_ID, API_HASH)

async def main():
    await client.start()
    channel = await client.get_entity(CHANNEL_USERNAME)

    last_id = get_last_id()
    count = 0

    async for message in client.iter_messages(
        channel,
        min_id=last_id,
        reverse=True
    ):
        if not (message.text or message.message):
            continue

        text = message.text or message.message
        link = f"https://t.me/{CHANNEL_USERNAME}/{message.id}"

        try:
            cursor.execute(
                "INSERT OR IGNORE INTO content (text, link) VALUES (?, ?)",
                (text, link)
            )
            conn.commit()
            save_last_id(message.id)

            count += 1
            print(f"Indexed {count}: {link}")

            if count >= BATCH_LIMIT:
                break

        except Exception as e:
            print("Error:", e)

        await asyncio.sleep(SLEEP_TIME)

    print("✅ Finished indexing batch")
    await client.disconnect()

asyncio.run(main())
