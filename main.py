"""eBay Marketplace Analyzer - Main Entry Point"""
import asyncio, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scraper import eBayScraper
from config import load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    examples = {
        "1": {"name": "iPhone 14 Pro", "input": {"search_query": "iPhone 14 Pro", "condition": "new", "max_listings": 50}},
        "2": {"name": "Gaming Laptops", "input": {"search_query": "gaming laptop", "min_price": 500, "max_price": 2000, "max_listings": 30}},
        "3": {"name": "Vintage Watches (sold)", "input": {"search_query": "vintage watches", "sold_listings": True, "max_listings": 25}},
        "4": {"name": "Free Shipping Electronics", "input": {"search_query": "electronics", "shipping": "free", "max_listings": 40}},
    }

    print("\n" + "="*60 + "\neBay Marketplace Analyzer\n" + "="*60)
    print("\nSelect an example:"), [print(f"  {k}. {v['name']}") for k, v in examples.items()]

    choice = input("\nChoice (1-4): ").strip()
    input_data = examples.get(choice, examples["1"])["input"]
    print(f"\nScraping: {input_data}\n")

    config = load_config()
    scraper = eBayScraper(proxy_config=config['proxy'], rate_limit=config['rate_limit'],
                         cache_config=config['cache'], output_dir=config['output_dir'])

    results = await scraper.run(input_data, export_formats=['json', 'csv'])

    if results:
        print(f"\n✓ Scraped {len(results)} listings")
        print(f"\nFirst listing:")
        listing = results[0]
        print(f"  Title: {listing['title'][:60]}...")
        print(f"  Price: ${listing['price']}")
        print(f"  Condition: {listing['condition']}")
        print(f"  Seller: {listing['seller']['username']}")
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(main())
