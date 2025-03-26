import asyncio
import aiohttp
from typing import Dict

class ViewAdder:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.success_count = 0
        self.error_count = 0
        self.active_proxies = set()

    async def add_view(self, session: aiohttp.ClientSession, post_url: str, proxy: str) -> bool:
        """
        Add a view to a Telegram post using TeaByte's method.
        Returns True if successful, False otherwise.
        """
        try:
            # Format proxy for aiohttp
            proxy_url = f"http://{proxy}"
            
            # Prepare the request
            async with session.get(
                post_url,
                proxy=proxy_url,
                headers=HEADERS,
                timeout=aiohttp.ClientTimeout(total=TIMEOUT),
                ssl=False
            ) as response:
                if response.status == 200:
                    self.success_count += 1
                    self.active_proxies.add(proxy)
                    return True
                else:
                    self.error_count += 1
                    return False

        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Error adding view with proxy {proxy}: {str(e)}")
            return False

    async def process_views(self, post_url: str, proxies: list, max_concurrent: int = 1000) -> Dict:
        """
        Process views using multiple proxies concurrently.
        """
        async with aiohttp.ClientSession() as session:
            tasks = []
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def bounded_add_view(proxy: str):
                async with semaphore:
                    return await self.add_view(session, post_url, proxy)

            # Create tasks for each proxy
            for proxy in proxies:
                task = asyncio.create_task(bounded_add_view(proxy))
                tasks.append(task)

            # Wait for all tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "success_count": self.success_count,
            "error_count": self.error_count,
            "active_proxies": len(self.active_proxies)
        }

    def get_stats(self) -> Dict:
        """
        Get current statistics
        """
        return {
            "views_added": self.success_count,
            "errors": self.error_count,
            "active_proxies": len(self.active_proxies)
        }

    def reset_stats(self):
        """
        Reset all statistics
        """
        self.success_count = 0
        self.error_count = 0
        self.active_proxies.clear()
