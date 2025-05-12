from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# File to store video URLs
VIDEO_FILE = "videos.txt"

# Initialize videos.txt if it doesn't exist
if not os.path.exists(VIDEO_FILE):
    with open(VIDEO_FILE, "w") as f:
        f.write("")

# Read videos from file
def read_videos():
    with open(VIDEO_FILE, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

# Write video to file
def add_video(url):
    with open(VIDEO_FILE, "a") as f:
        f.write(url + "\n")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to M3U8ss Bot! Use:\n/add <url> - Add an .m3u8 video URL\n/list - List all videos\n/play <index> - Play a video\n/help - Show this help"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n/add <url> - Add an .m3u8 video URL\n/list - List all video URLs\n/play <index> - Play video by index\n/start - Start the bot\n/help - Show this help"
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a video URL: /add <url>")
        return
    url = context.args[0]
    if not url.endswith(".m3u8"):
        await update.message.reply_text("Please provide a valid .m3u8 URL.")
        return
    add_video(url)
    await update.message.reply_text(f"Added video: {url}")

async def list_videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    videos = read_videos()
    if not videos:
        await update.message.reply_text("No videos added yet. Use /add <url> to add one.")
        return
    response = "Available videos:\n" + "\n".join(f"{i+1}. {url}" for i, url in enumerate(videos))
    await update.message.reply_text(response)

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    videos = read_videos()
    if not videos:
        await update.message.reply_text("No videos available. Use /add <url> to add one.")
        return
    if not context.args:
        await update.message.reply_text("Please provide a video index: /play <index>")
        return
    try:
        index = int(context.args[0]) - 1
        if 0 <= index < len(videos):
            await update.message.reply_video(
                video=videos[index],
                caption="M3U8 video. Feel free to forward!",
                supports_streaming=True
            )
        else:
            await update.message.reply_text("Invalid index. Use /list to see available videos.")
    except ValueError:
        await update.message.reply_text("Please provide a valid number: /play <index>")

def main():
    logger.info("Starting the bot application with polling")
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_videos))
    app.add_handler(CommandHandler("play", play))

    logger.info("Starting polling")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
