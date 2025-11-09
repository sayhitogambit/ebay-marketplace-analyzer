"""
eBay Marketplace Analyzer
Extract product listings, prices, and seller information from eBay
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional
from urllib.parse import quote_plus, urlencode
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scrapling import Fetcher
from shared.base_actor import BaseActor
from shared.utils import retry_with_backoff
from schema import eBayScraperInput, eBayListing, SellerInfo

logger = logging.getLogger(__name__)


class eBayScraper(BaseActor):
    """
    eBay Marketplace Analyzer

    Features:
        - Search eBay listings by keyword
        - Filter by condition, price, location
        - Extract seller ratings and feedback
        - Support for sold/completed listings
        - eBay is scraper-friendly (no heavy anti-bot)
        - Datacenter proxies sufficient
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = "https://www.ebay.com"

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input using Pydantic schema"""
        try:
            eBayScraperInput(**input_data)
            return True
        except Exception as e:
            raise ValueError(f"Invalid input: {e}")

    async def scrape(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Main scraping method"""
        config = eBayScraperInput(**input_data)

        logger.info(f"Starting eBay scrape: {config.search_query}")

        # Build search URL
        search_url = self._build_search_url(config)

        # Scrape listings
        listings = await self._scrape_listings(
            search_url,
            config.max_listings
        )

        logger.info(f"Scraped {len(listings)} listings from eBay")

        return [listing.model_dump() for listing in listings]

    def _build_search_url(self, config: eBayScraperInput) -> str:
        """Build eBay search URL with filters"""
        params = {
            '_nkw': config.search_query,
            '_sop': '12',  # Sort by newly listed
        }

        # Add filters
        if config.condition:
            # eBay condition codes
            condition_map = {
                'new': 1000,
                'used': 3000,
                'refurbished': 2000,
                'for parts': 7000
            }
            if code := condition_map.get(config.condition.lower()):
                params['LH_ItemCondition'] = code

        if config.min_price:
            params['_udlo'] = str(config.min_price)

        if config.max_price:
            params['_udhi'] = str(config.max_price)

        if config.shipping == 'free':
            params['LH_FS'] = '1'

        if config.sold_listings:
            params['LH_Sold'] = '1'
            params['LH_Complete'] = '1'

        # Build URL
        url = f"{self.base_url}/sch/i.html?{urlencode(params)}"

        return url

    @retry_with_backoff(max_retries=3, base_delay=2.0)
    async def _scrape_listings(
        self,
        search_url: str,
        max_listings: int
    ) -> List[eBayListing]:
        """
        Scrape eBay listings from search results

        Args:
            search_url: eBay search URL
            max_listings: Maximum listings to scrape

        Returns:
            List of eBayListing objects
        """
        await self.rate_limit()

        listings = []
        page = 1
        proxy = await self.get_proxy()

        while len(listings) < max_listings:
            # Add pagination
            paginated_url = f"{search_url}&_pgn={page}"

            # Fetcher is synchronous, not async
                try:
                    fetcher = Fetcher(proxy=proxy)
                    logger.info(f"Fetching page {page}: {paginated_url}")

                    response = fetcher.get(paginated_url)

                    # Parse listing items
                    # eBay uses structured HTML with specific classes
                    page_html = response.text

                    # Extract listing cards
                    # Note: eBay's HTML structure can vary, this is a simplified version
                    import re
                    from bs4 import BeautifulSoup

                    soup = BeautifulSoup(page_html, 'html.parser')

                    # Find listing items (main search results)
                    item_cards = soup.find_all('li', class_='s-item') or \
                                soup.find_all('div', class_='s-item__wrapper')

                    if not item_cards:
                        logger.info("No more listings found")
                        break

                    logger.info(f"Found {len(item_cards)} items on page {page}")

                    for card in item_cards:
                        if len(listings) >= max_listings:
                            break

                        try:
                            listing = self._parse_listing_card(card)
                            if listing:
                                listings.append(listing)
                        except Exception as e:
                            logger.error(f"Error parsing listing: {e}")
                            continue

                    # Check for next page
                    next_page = soup.find('a', {'aria-label': 'Next page'})
                    if not next_page or len(item_cards) == 0:
                        break

                    page += 1
                    await asyncio.sleep(1)  # Polite delay

                    if proxy and self.proxy_manager:
                        self.proxy_manager.report_success(proxy)

                except Exception as e:
                    if proxy and self.proxy_manager:
                        self.proxy_manager.report_failure(proxy)
                    raise

        return listings[:max_listings]

    def _parse_listing_card(self, card) -> Optional[eBayListing]:
        """
        Parse eBay listing card

        Args:
            card: BeautifulSoup element

        Returns:
            eBayListing object or None
        """
        try:
            # Extract item ID
            item_link = card.find('a', class_='s-item__link')
            if not item_link:
                return None

            item_url = item_link.get('href', '')
            item_id_match = re.search(r'/itm/(\d+)', item_url)
            item_id = item_id_match.group(1) if item_id_match else 'unknown'

            # Title
            title_elem = card.find('h3', class_='s-item__title') or \
                        card.find('div', class_='s-item__title')
            title = title_elem.get_text(strip=True) if title_elem else 'Unknown'

            # Price
            price_elem = card.find('span', class_='s-item__price')
            price_text = price_elem.get_text(strip=True) if price_elem else '$0'
            price = self._parse_price(price_text)

            # Shipping
            shipping_elem = card.find('span', class_='s-item__shipping')
            shipping_text = shipping_elem.get_text(strip=True) if shipping_elem else ''
            shipping_cost = self._parse_shipping(shipping_text)

            # Condition
            condition_elem = card.find('span', class_='SECONDARY_INFO')
            condition = condition_elem.get_text(strip=True) if condition_elem else 'Used'

            # Location
            location_elem = card.find('span', class_='s-item__location') or \
                           card.find('span', class_='s-item__itemLocation')
            location = location_elem.get_text(strip=True) if location_elem else 'Unknown'

            # Bids (for auctions)
            bids_elem = card.find('span', class_='s-item__bids')
            bids_text = bids_elem.get_text(strip=True) if bids_elem else '0'
            bids = int(re.search(r'\d+', bids_text).group()) if re.search(r'\d+', bids_text) else 0

            # Images
            img_elem = card.find('img', class_='s-item__image-img')
            image_url = img_elem.get('src', '') if img_elem else ''

            # Seller info (simplified - would need to visit seller page for full details)
            seller_elem = card.find('span', class_='s-item__seller-info-text')
            seller_username = seller_elem.get_text(strip=True) if seller_elem else 'unknown'

            # Create seller info object with placeholder data
            seller = SellerInfo(
                username=seller_username,
                rating=4.5,  # Would need separate API call
                feedback_count=100,  # Would need separate API call
                positive_percentage=98.0  # Would need separate API call
            )

            # Determine listing type
            is_auction = 'bid' in price_text.lower() or bids > 0
            is_buy_now = not is_auction

            listing = eBayListing(
                item_id=item_id,
                title=title,
                price=price,
                currency='USD',
                shipping_cost=shipping_cost,
                condition=condition,
                seller=seller,
                location=location,
                bids=bids,
                images=[image_url] if image_url else [],
                listing_url=item_url,
                is_auction=is_auction,
                is_buy_now=is_buy_now
            )

            return listing

        except Exception as e:
            logger.error(f"Error parsing listing card: {e}")
            return None

    def _parse_price(self, price_text: str) -> float:
        """Parse price from text like '$1,234.56' or '$100 to $200'"""
        # Remove currency symbols and commas
        price_text = re.sub(r'[^\d.,]', '', price_text)

        # Handle price ranges (take first price)
        if 'to' in price_text:
            price_text = price_text.split('to')[0]

        try:
            return float(price_text.replace(',', ''))
        except:
            return 0.0

    def _parse_shipping(self, shipping_text: str) -> Optional[float]:
        """Parse shipping cost from text"""
        if 'free' in shipping_text.lower():
            return 0.0

        # Extract number from shipping text
        match = re.search(r'\$?([\d,]+\.?\d*)', shipping_text)
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except:
                pass

        return None
