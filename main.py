import os
import asyncio
from aiohttp import web
from hydrogram import Client, filters, idle
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID
import database as db

app = Client("head_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text("Welcome! Send your access key to set up your bot.")

@app.on_message(filters.command("genkey") & filters.user(OWNER_ID))
async def gen_key(client, message):
    import secrets
    key = f"KEY-{secrets.token_hex(4).upper()}"
    await db.add_key(key)
    await message.reply_text(f"Generated Key: `{key}`")

@app.on_message(filters.private & filters.text)
async def handle_text(client, message):
    text = message.text.strip()
    if text.startswith("KEY-"):
        if await db.is_key_valid(text):
            await db.use_key(text, message.from_user.id)
            await message.reply_text("Key verified! Now send your Sub-Bot Token.")
        else:
            await message.reply_text("Invalid or used key.")

async def handle_web(request):
    return web.Response(text="Bot Alive!")

async def main():
    # Web server logic for Render
    server = web.Application()
    server.router.add_get("/", handle_web)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    # Start Hydrogram Client
    await app.start()
    print("Bot is live and running!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
