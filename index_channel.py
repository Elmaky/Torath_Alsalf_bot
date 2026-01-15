import os
import asyncio
import sqlite3
from telethon import TelegramClient

# ====== Environment Variables (Railway) ======
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "meknaz_alalbany")

# ====== Database ======
conn = sqlite3.connect("content.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    link TEXT
)
""")
conn.commit()

# ====== Telegram Client ======
client = TelegramClient("session", API_ID, API_HASH)

async def main():
    await client.start()

    channel = await client.get_entity(CHANNEL_USERNAME)

    offset_id = 0
    total = 0
    BATCH = 100

    while True:
        messages = await client.get_messages(
            channel,
            limit=BATCH,
            offset_id=offset_id
        )

        if not messages:
            break

        for msg in messages:
            offset_id = msg.id

            if msg.text:
                link = f"https://t.me/{CHANNEL_USERNAME}/{msg.id}"
                cursor.execute(
                    "INSERT INTO content (text, link) VALUES (?, ?)",
                    (msg.text, link)
                )
                total += 1

                if total % 100 == 0:
                    print(f"Indexed {total}")

        conn.commit()
        await asyncio.sleep(1)

    print("✅ FULL INDEXING FINISHED")
    await client.disconnect()

asyncio.run(main())
