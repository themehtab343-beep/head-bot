import os
import secrets
from fastapi import FastAPI
import uvicorn
from hydrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID
import database as db

web_app = FastAPI()
bot_app = Client("head_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot_app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text("Welcome! Send your access key to set up your bot.")

@bot_app.on_message(filters.command("genkey") & filters.user(OWNER_ID))
async def gen_key(client, message):
    key = f"KEY-{secrets.token_hex(4).upper()}"
    await db.add_key(key)
    await message.reply_text(f"Generated Key: `{key}`")

@bot_app.on_message(filters.private & filters.text)
async def handle_text(client, message):
    text = message.text.strip()
    if text.startswith("KEY-"):
        if await db.is_key_valid(text):
            await db.use_key(text, message.from_user.id)
            await message.reply_text("Key verified! Now send your Sub-Bot Token.")
        else:
            await message.reply_text("Invalid or used key.")

@web_app.on_event("startup")
async def start_bot():
    await bot_app.start()

@web_app.on_event("shutdown")
async def stop_bot():
    await bot_app.stop()

@web_app.get("/")
def read_root():
    return {"status": "Bot Alive"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(web_app, host="0.0.0.0", port=port)
