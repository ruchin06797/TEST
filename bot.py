import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Initialize bot
app = Client(
    "file_stream_bot",
    api_id=os.getenv("API_ID"),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

# Cloudflare Worker URL (set in Railway variables)
WORKER_URL = os.getenv("WORKER_URL", "https://your-worker.workers.dev")

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("📁 Send me any file to generate a streaming link")

@app.on_message(filters.document | filters.video | filters.audio)
async def handle_file(client, message):
    try:
        file = message.document or message.video or message.audio
        if not file.file_name:
            return await message.reply("⚠️ Unnamed files not supported")
            
        # Get direct download URL
        file_msg = await client.get_messages(message.chat.id, message.id)
        file_url = await file_msg.download()
        
        # Create streaming URL
        stream_url = f"{WORKER_URL}?url={file_url}&name={file.file_name}"
        
        # Send to user
        await message.reply(
            f"**🔗 Streaming Link Ready**\n\n"
            f"📂 File: `{file.file_name}`\n"
            f"⚡ Instant streaming available\n\n",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("▶️ Stream Now", url=stream_url)],
                [InlineKeyboardButton("📥 Direct Download", url=file_url)]
            ]),
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

print("Bot is running...")
app.run()
