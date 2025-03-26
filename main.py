import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Optional
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot and components
bot = AsyncTeleBot(BOT_TOKEN)
proxy_scraper = ProxyScraper()
view_adder = ViewAdder()

# Store active tasks and their status
active_tasks: Dict[int, Dict] = {}

def validate_telegram_url(url: str) -> bool:
    """Validate if the URL is a valid Telegram post URL."""
    pattern = r'^https?:\/\/t\.me\/[a-zA-Z0-9_]+\/\d+$'
    return bool(re.match(pattern, url))

async def update_status_message(chat_id: int, message_id: int, task_info: Dict):
    """Update the status message with current progress."""
    try:
        stats = view_adder.get_stats()
        uptime = datetime.now() - task_info['start_time']
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds

        status_text = STATUS_MESSAGE.format(
            views=stats['views_added'],
            active_proxies=stats['active_proxies'],
            errors=stats['errors'],
            uptime=uptime_str,
            threads=THREAD_COUNT
        )

        await bot.edit_message_text(
            status_text,
            chat_id=chat_id,
            message_id=message_id
        )
    except Exception as e:
        logger.error(f"Error updating status: {str(e)}")

async def process_views_task(chat_id: int, message_id: int, post_url: str):
    """Process views addition task."""
    try:
        # Initial status message
        status_msg = await bot.send_message(chat_id, "🚀 Initializing view addition process...")

        async def update_status(text: str):
            """Callback function to update status message."""
            try:
                await bot.edit_message_text(
                    text,
                    chat_id=chat_id,
                    message_id=status_msg.message_id
                )
            except Exception as e:
                logger.error(f"Error updating status: {str(e)}")

        # Scrape proxies with status updates
        proxies = await proxy_scraper.scrape(status_callback=update_status)

        if not proxies:
            await update_status("❌ No working proxies found. Please try again later.")
            return

        # Initialize task info
        task_info = {
            'start_time': datetime.now(),
            'status_message_id': status_msg.message_id
        }
        active_tasks[chat_id] = task_info

        # Start view adding process
        await update_status(
            f"🚀 Starting View Addition:\n"
            f"• Working Proxies: {len(proxies)}\n"
            f"• Thread Count: {THREAD_COUNT}\n"
            f"• Target URL: {post_url}\n\n"
            f"Starting workers..."
        )

        # Start status update loop
        update_task = asyncio.create_task(status_update_loop(chat_id, status_msg.message_id, task_info))

        # Process views
        result = await view_adder.process_views(post_url, proxies, THREAD_COUNT)

        # Cancel status update loop
        update_task.cancel()
        
        # Send final status
        stats = view_adder.get_stats()
        final_message = f"""
✅ Task Completed!

📊 Final Statistics:
• Total Views Added: {stats['views_added']}
• Active Proxies Used: {stats['active_proxies']}
• Errors Encountered: {stats['errors']}
• Total Time: {datetime.now() - task_info['start_time']}
"""
        await update_status(final_message)

    except Exception as e:
        logger.error(f"Error in process_views_task: {str(e)}")
        await bot.send_message(
            chat_id,
            f"❌ An error occurred: {str(e)}\nPlease try again."
        )
    finally:
        # Cleanup
        if chat_id in active_tasks:
            del active_tasks[chat_id]
        view_adder.reset_stats()

async def status_update_loop(chat_id: int, message_id: int, task_info: Dict):
    """Periodically update the status message."""
    try:
        while True:
            await update_status_message(chat_id, message_id, task_info)
            await asyncio.sleep(3)  # Update every 3 seconds
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Error in status update loop: {str(e)}")

@bot.message_handler(commands=['start'])
async def start_handler(message: Message):
    """Handle /start command."""
    try:
        await bot.reply_to(message, WELCOME_MESSAGE)
    except Exception as e:
        logger.error(f"Error in start handler: {str(e)}")

@bot.message_handler(func=lambda message: True)
async def message_handler(message: Message):
    """Handle incoming messages (expecting Telegram post URL)."""
    try:
        # Check if user has an active task
        if message.chat.id in active_tasks:
            await bot.reply_to(
                message,
                "⚠️ You have an active task running. Please wait for it to complete."
            )
            return

        # Validate URL
        if not validate_telegram_url(message.text):
            await bot.reply_to(
                message,
                "❌ Invalid URL format. Please send a valid Telegram post URL.\n"
                "Example: https://t.me/channel_name/123"
            )
            return

        # Start processing
        await process_views_task(message.chat.id, message.message_id, message.text)

    except Exception as e:
        logger.error(f"Error in message handler: {str(e)}")
        await bot.reply_to(
            message,
            f"❌ An error occurred: {str(e)}\nPlease try again."
        )

async def main():
    """Main function to run the bot."""
    try:
        logger.info("Starting bot...")
        await bot.polling(non_stop=True)
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
