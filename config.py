"""eBay Scraper - Configuration"""
import os
from dotenv import load_dotenv

load_dotenv()

def load_config():
    return {
        'proxy': {
            'enabled': os.getenv('PROXY_ENABLED', 'false').lower() == 'true',  # Optional for eBay
            'proxies': _parse_proxies(),
            'rotation_strategy': os.getenv('PROXY_ROTATION_STRATEGY', 'round_robin')
        },
        'rate_limit': {
            'max_requests': int(os.getenv('RATE_LIMIT_REQUESTS', '30')),
            'time_window': int(os.getenv('RATE_LIMIT_WINDOW', '60'))
        },
        'cache': {
            'enabled': os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
            'cache_dir': os.getenv('CACHE_DIR', '.cache/ebay'),
            'ttl': int(os.getenv('CACHE_TTL', '3600'))
        },
        'output_dir': os.getenv('OUTPUT_DIR', 'output/ebay'),
        'log_level': os.getenv('LOG_LEVEL', 'INFO')
    }

def _parse_proxies():
    proxies = []
    if server := os.getenv('PROXY_SERVER'):
        proxy_config = {'server': server}
        if (username := os.getenv('PROXY_USERNAME')) and (password := os.getenv('PROXY_PASSWORD')):
            proxy_config.update({'username': username, 'password': password})
        proxies.append(proxy_config)
    return proxies
