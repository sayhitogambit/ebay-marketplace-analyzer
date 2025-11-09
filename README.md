# eBay Marketplace Analyzer

Extract product listings, prices, seller ratings, and market data from eBay.

## Features

- 🛍️ Search eBay by keyword
- 💰 Price filtering (min/max)
- ✅ Condition filters (new, used, refurbished)
- 📦 Shipping options (free shipping filter)
- 📊 Sold listings analysis
- ⭐ Seller ratings and feedback
- 🚀 Scraper-friendly (minimal anti-bot)

## Installation

```bash
pip install -r ../../requirements.txt
pip install beautifulsoup4  # Required for eBay
```

## Usage

```python
from scraper import eBayScraper

scraper = eBayScraper()
results = await scraper.run({
    "search_query": "iPhone 14 Pro",
    "condition": "new",
    "max_listings": 50
})
```

## Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search_query` | string | required | Search keyword |
| `category` | string | None | eBay category |
| `condition` | string | None | new, used, refurbished |
| `min_price` | float | None | Minimum price |
| `max_price` | float | None | Maximum price |
| `location` | string | None | Location filter |
| `shipping` | string | None | free, local |
| `sold_listings` | bool | false | Include sold items |
| `max_listings` | int | 100 | Max items (1-1000) |

## Output Schema

```json
{
  "item_id": "123456789",
  "title": "iPhone 14 Pro 256GB",
  "price": 899.99,
  "shipping_cost": 0.0,
  "condition": "New",
  "seller": {
    "username": "bestseller",
    "rating": 4.9,
    "feedback_count": 5000,
    "positive_percentage": 99.5
  },
  "location": "California, USA",
  "bids": 0,
  "is_buy_now": true,
  "listing_url": "https://..."
}
```

## Best Practices

1. **No Proxies Needed**: eBay is relatively scraper-friendly
2. **Rate Limiting**: 30 requests/minute is safe
3. **Caching**: Enable for price tracking over time
4. **Sold Listings**: Great for market research

## Limitations

- Seller details require additional page visits
- Some data may be approximate
- International sites require different base URL

---

**Difficulty:** EASY (3-4 days)
**Users:** 35K | **Rating:** ⭐4.3
