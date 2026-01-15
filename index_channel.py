from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import sqlite3
import asyncio
import os

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
CHANNEL_USERNAME = "meknaz_alalbany"  # بدون @

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

client = TelegramClient("session", API_ID, API_HASH)

async def main():
    await client.start()
    channel = await client.get_entity(CHANNEL_USERNAME)

    offset_id = 0
    count = 0

    while True:
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=100,
            max_id=0,
            min_id=0,
            hash=0
        ))

        if not history.messages:
            break

        for message in history.messages:
            text = message.text or message.message
            if text:
                link = f"https://t.me/{CHANNEL_USERNAME}/{message.id}"
                cursor.execute(
                    "INSERT INTO content (text, link) VALUES (?, ?)",
                    (text, link)
                )
                count += 1
                print(f"Indexed {count}: {link}")

            offset_id = message.id

        conn.commit()
        await asyncio.sleep(1)

    print("✅ Finished indexing")
    await client.disconnect()

asyncio.run(main())
