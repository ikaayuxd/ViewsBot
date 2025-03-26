
# Bot Configuration
BOT_TOKEN = "6590125561:AAHph8L_ZrB2UnBp4Zswi-XHUjdo5ROaOZs"
THREAD_COUNT = 800  # Number of threads for view adding
TIMEOUT = 10  # Timeout for requests in seconds

# Request Headers
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0"
}

# Proxy Sources
PROXY_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt"
]

# Telegram Messages
WELCOME_MESSAGE = """
👋 Welcome to the Telegram Views Bot!

Send me a Telegram post link and I'll start adding views to it.
The process will use multiple proxies and threads for maximum efficiency.

Usage:
1. Send me a Telegram post link
2. Wait for the process to start
3. You'll receive real-time updates on the progress

Example link format: https://t.me/channel_name/post_id
"""

STATUS_MESSAGE = """
📊 Current Status:
• Views Added: {views}
• Active Proxies: {active_proxies}
• Errors: {errors}
• Uptime: {uptime}
• Threads: {threads}

🔄 Process is running...
"""
