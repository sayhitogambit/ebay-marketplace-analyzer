"""
eBay Marketplace Analyzer - Input/Output Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class eBayScraperInput(BaseModel):
    """Input schema for eBay Scraper"""

    search_query: str = Field(
        ...,
        description="Search query for eBay items",
        example="iPhone 14 Pro"
    )

    category: Optional[str] = Field(
        None,
        description="eBay category ID or name",
        example="Electronics"
    )

    condition: Optional[str] = Field(
        None,
        description="Item condition: new, used, refurbished"
    )

    min_price: Optional[float] = Field(
        None,
        ge=0,
        description="Minimum price filter"
    )

    max_price: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum price filter"
    )

    location: Optional[str] = Field(
        None,
        description="Location filter",
        example="United States"
    )

    shipping: Optional[str] = Field(
        None,
        description="Shipping filter: free, local"
    )

    sold_listings: bool = Field(
        False,
        description="Include sold/completed listings"
    )

    max_listings: int = Field(
        100,
        ge=1,
        le=1000,
        description="Maximum listings to scrape"
    )

    @validator('condition')
    def validate_condition(cls, v):
        if v:
            valid = ['new', 'used', 'refurbished', 'for parts']
            if v.lower() not in valid:
                raise ValueError(f"condition must be one of: {valid}")
        return v


class SellerInfo(BaseModel):
    """eBay seller information"""
    username: str
    rating: float
    feedback_count: int
    positive_percentage: float


class eBayListing(BaseModel):
    """eBay listing schema"""
    item_id: str
    title: str
    price: float
    currency: str = "USD"
    shipping_cost: Optional[float] = None
    condition: str
    seller: SellerInfo
    location: str
    bids: int = 0
    watchers: Optional[int] = None
    time_left: Optional[str] = None
    images: List[str] = []
    description: str = ""
    item_specifics: Dict[str, str] = {}
    shipping_options: List[Dict[str, Any]] = []
    return_policy: Optional[str] = None
    listing_url: str
    is_auction: bool = False
    is_buy_now: bool = False
    sold_date: Optional[str] = None  # For sold listings
    sold_price: Optional[float] = None  # For sold listings

    class Config:
        json_schema_extra = {
            "example": {
                "item_id": "123456789",
                "title": "iPhone 14 Pro 256GB - Space Black",
                "price": 899.99,
                "condition": "New",
                "seller": {
                    "username": "bestseller",
                    "rating": 4.9,
                    "feedback_count": 5000,
                    "positive_percentage": 99.5
                },
                "location": "California, USA",
                "bids": 0,
                "is_buy_now": True
            }
        }
