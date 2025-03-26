import requests
import re
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Set, Optional, Callable

class ProxyScraper:
    def __init__(self):
        self.proxies: Set[str] = set()
        self.logger = logging.getLogger(__name__)

    async def fetch_proxy_list(self, url: str) -> Set[str]:
        """Fetch proxies from a given URL."""
        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
            
            # Extract proxies using regex pattern
            proxy_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}:\d{1,5}\b'
            found_proxies = set(re.findall(proxy_pattern, response.text))
            
            self.logger.info(f"Found {len(found_proxies)} proxies from {url}")
            return found_proxies
        
        except Exception as e:
            self.logger.error(f"Error fetching proxies from {url}: {str(e)}")
            return set()

    def test_proxy(self, proxy: str) -> bool:
        """Test if a proxy is working."""
        try:
            test_url = "https://t.me"
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
            response = requests.get(
                test_url,
                proxies=proxies,
                headers=HEADERS,
                timeout=TIMEOUT
            )
            return response.status_code == 200
        except:
            return False

    async def scrape(self, status_callback: Optional[Callable] = None) -> List[str]:
        """Scrape proxies from all sources and test them."""
        # Fetch proxies from all sources
        total_found = 0
        if status_callback:
            await status_callback("🔍 Starting proxy scraping from multiple sources...")
            
        for source in PROXY_SOURCES:
            if status_callback:
                await status_callback(f"📥 Fetching proxies from source: {source.split('/')[-2]}")
            new_proxies = await self.fetch_proxy_list(source)
            self.proxies.update(new_proxies)
            total_found += len(new_proxies)
            if status_callback:
                await status_callback(
                    f"Found {len(new_proxies)} proxies from current source\n"
                    f"Total unique proxies so far: {len(self.proxies)}"
                )

        status_msg = (
            f"📊 Proxy Collection Complete:\n"
            f"• Total unique proxies: {len(self.proxies)}\n"
            f"• Total (with duplicates): {total_found}"
        )
        self.logger.info(status_msg)
        if status_callback:
            await status_callback(status_msg)

        # Test proxies concurrently
        working_proxies = []
        tested_count = 0
        total_proxies = len(self.proxies)
        
        test_msg = (
            f"\n🔍 Starting proxy testing with 50 concurrent workers...\n"
            f"• Total proxies to test: {total_proxies}"
        )
        self.logger.info(test_msg)
        if status_callback:
            await status_callback(test_msg)
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            future_to_proxy = {
                executor.submit(self.test_proxy, proxy): proxy 
                for proxy in self.proxies
            }
            
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                tested_count += 1
                
                if tested_count % 50 == 0:  # Update more frequently
                    progress_msg = (
                        f"🔄 Testing Progress:\n"
                        f"• Tested: {tested_count}/{total_proxies}\n"
                        f"• Working: {len(working_proxies)}\n"
                        f"• Progress: {(tested_count/total_proxies*100):.1f}%"
                    )
                    self.logger.info(progress_msg)
                    if status_callback:
                        await status_callback(progress_msg)
                
                try:
                    if future.result():
                        working_proxies.append(proxy)
                except Exception as e:
                    self.logger.error(f"Error testing proxy {proxy}: {str(e)}")

        success_rate = (len(working_proxies) / total_proxies * 100) if total_proxies > 0 else 0
        final_msg = (
            f"✅ Proxy Testing Completed:\n"
            f"• Total Tested: {total_proxies}\n"
            f"• Working Proxies: {len(working_proxies)}\n"
            f"• Success Rate: {success_rate:.1f}%"
        )
        self.logger.info(final_msg)
        if status_callback:
            await status_callback(final_msg)
        
        return working_proxies

    def get_working_proxies(self) -> List[str]:
        """Get a list of working proxies."""
        return list(self.proxies)
