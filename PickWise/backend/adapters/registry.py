"""
Adapter Registry and URL Router for PickWise.
Handles URL validation, deduplication, 30-minute caching,
and resilient per-link extraction.
"""

import re
from urllib.parse import urlparse
from typing import Dict, List, Any, Optional, Tuple
from backend.cache.simple_cache import GLOBAL_CACHE
from .flipkart import FlipkartAdapter
from .amazon import AmazonAdapter
from .base import BaseAdapter

class AdapterRegistry:
    def __init__(self):
        self.adapters: List[BaseAdapter] = [
            FlipkartAdapter(),
            AmazonAdapter()
        ]

    def get_adapter(self, url: str) -> Optional[BaseAdapter]:
        try:
            parsed = urlparse(url.strip())
            netloc = parsed.netloc.lower()
            for adapter in self.adapters:
                if any(domain in netloc for domain in adapter.domains):
                    return adapter
        except Exception:
            pass
        return None

    def validate_urls(self, urls: List[str]) -> Tuple[bool, Optional[str], List[str]]:
        """
        Validates URL batch:
        - 2 to 5 links required
        - No empty strings
        - Valid URL format
        - Supported e-commerce domains
        - No duplicates
        """
        if not urls or len(urls) < 2:
            return False, "Please enter at least 2 product links to compare.", []
        if len(urls) > 5:
            return False, "You can compare up to 5 product links at a time.", []

        cleaned_urls = []
        normalized_set = set()

        for idx, u in enumerate(urls):
            if not u or not isinstance(u, str):
                return False, f"Link #{idx+1} is empty.", []
            trimmed = u.strip()
            if not (trimmed.startswith("http://") or trimmed.startswith("https://")):
                return False, f"Link #{idx+1} ('{trimmed[:30]}...') is not a valid URL. Must start with http:// or https://.", []

            adapter = self.get_adapter(trimmed)
            if not adapter:
                return False, f"Link #{idx+1} is from an unsupported store. Currently Flipkart and Amazon are supported.", []

            # Normalize for deduplication (strip query params if possible or lower)
            parsed = urlparse(trimmed)
            normalized_key = f"{parsed.netloc}{parsed.path}".rstrip("/").lower()

            if normalized_key in normalized_set:
                return False, f"Duplicate product link detected at position #{idx+1}. Please provide distinct products.", []

            normalized_set.add(normalized_key)
            cleaned_urls.append(trimmed)

        return True, None, cleaned_urls

    def extract_product(self, url: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Extracts product details with 30-min cache and per-link fallback handling.
        Never throws unhandled exceptions.
        """
        cache_key = f"pickwise:product:{url.strip()}"
        if not force_refresh:
            cached = GLOBAL_CACHE.get(cache_key)
            if cached:
                cached_copy = dict(cached)
                cached_copy["from_cache"] = True
                return cached_copy

        adapter = self.get_adapter(url)
        if not adapter:
            return {
                "id": url,
                "url": url,
                "name": "Unsupported Store Link",
                "brand": "Unknown",
                "image": "",
                "specs": {},
                "status": "needs_fallback",
                "error": "Store adapter not found. You can enter specifications manually.",
                "from_cache": False
            }

        try:
            html, fetch_err = adapter.fetch(url)
            parsed_data = adapter.parse(url, html)
            if fetch_err:
                parsed_data["status"] = "needs_fallback"
                parsed_data["error"] = fetch_err

            # Assign unique ID
            parsed_data["id"] = url
            parsed_data["from_cache"] = False

            # Cache the result for 30 minutes
            GLOBAL_CACHE.set(cache_key, parsed_data)
            return parsed_data

        except Exception as e:
            fallback_obj = {
                "id": url,
                "url": url,
                "name": "Product Link (Extraction Failed)",
                "brand": "Unknown",
                "image": "",
                "specs": {},
                "status": "needs_fallback",
                "error": f"Extraction error: {str(e)[:100]}. Please provide specs manually.",
                "from_cache": False
            }
            return fallback_obj

    def extract_batch(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Extracts all products sequentially or concurrently."""
        results = []
        for url in urls:
            res = self.extract_product(url)
            results.append(res)
        return results

REGISTRY = AdapterRegistry()
