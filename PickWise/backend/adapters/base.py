"""
Base adapter class for PickWise web scrapers.
Implements polite headers, structured data JSON-LD extraction,
and common regex extractors for mobile specs.
"""

import json
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, Tuple

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

class BaseAdapter:
    site_name: str = "Generic"
    domains: list = []

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENTS[0],
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        })

    def fetch(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetches page HTML.
        Returns (html_content, error_message).
        Never raises exceptions.
        """
        try:
            resp = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            if resp.status_code == 200:
                return resp.text, None
            elif resp.status_code in (403, 429, 503):
                return None, f"Website returned anti-bot status {resp.status_code}. Fallback required."
            else:
                return None, f"HTTP Error {resp.status_code}"
        except requests.exceptions.Timeout:
            return None, "Request timed out after 10 seconds. Fallback required."
        except Exception as e:
            return None, f"Connection error: {str(e)[:80]}. Fallback required."

    def extract_json_ld(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Scans for application/ld+json and extracts Product schema."""
        data = {}
        for script in soup.find_all("script", type="application/ld+json"):
            if not script.string:
                continue
            try:
                parsed = json.loads(script.string.strip())
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, dict) and item.get("@type") == "Product":
                            return item
                elif isinstance(parsed, dict):
                    if parsed.get("@type") == "Product":
                        return parsed
                    # Check graph array
                    graph = parsed.get("@graph")
                    if isinstance(graph, list):
                        for item in graph:
                            if isinstance(item, dict) and item.get("@type") == "Product":
                                return item
            except Exception:
                continue
        return data

    def parse(self, url: str, html: Optional[str]) -> Dict[str, Any]:
        """Subclasses must implement parse."""
        raise NotImplementedError

    # Shared regex utility helpers
    @staticmethod
    def extract_ram_gb(text: str) -> Optional[int]:
        if not text:
            return None
        m = re.search(r'(\d+)\s*(?:GB|gb)\s*(?:RAM|ram)', text, re.IGNORECASE)
        if m:
            return int(m.group(1))
        # Fallback e.g. "12 GB"
        m = re.search(r'(\d+)\s*GB', text, re.IGNORECASE)
        if m and int(m.group(1)) in (2, 3, 4, 6, 8, 12, 16, 24, 32):
            return int(m.group(1))
        return None

    @staticmethod
    def extract_storage_gb(text: str) -> Optional[int]:
        if not text:
            return None
        # Check TB first
        m_tb = re.search(r'(\d+)\s*TB', text, re.IGNORECASE)
        if m_tb:
            return int(m_tb.group(1)) * 1024
        m = re.search(r'(\d+)\s*(?:GB|gb)\s*(?:ROM|Storage|internal)', text, re.IGNORECASE)
        if m:
            return int(m.group(1))
        # Look for standard mobile storage sizes
        m2 = re.findall(r'(\d+)\s*GB', text, re.IGNORECASE)
        for val in m2:
            num = int(val)
            if num in (32, 64, 128, 256, 512):
                return num
        return None

    @staticmethod
    def extract_battery_mah(text: str) -> Optional[int]:
        if not text:
            return None
        m = re.search(r'(\d{4,5})\s*mAh', text, re.IGNORECASE)
        if m:
            return int(m.group(1))
        return None

    @staticmethod
    def extract_charging_w(text: str) -> Optional[int]:
        if not text:
            return None
        m = re.search(r'(\d{1,3})\s*W\b', text, re.IGNORECASE)
        if m:
            return int(m.group(1))
        return None

    @staticmethod
    def extract_camera_mp(text: str) -> Tuple[Optional[int], Optional[int]]:
        """Extracts (rear_mp, front_mp)."""
        rear = None
        front = None
        if not text:
            return rear, front
        
        # Rear camera match: "50MP", "50 MP + 8 MP"
        m_rear = re.search(r'(\d{1,3})\s*MP(?:\s*\+\s*\d+\s*MP)*\s*(?:Rear|Primary|Back)?', text, re.IGNORECASE)
        if m_rear:
            rear = int(m_rear.group(1))
        
        m_front = re.search(r'(\d{1,3})\s*MP\s*(?:Front|Selfie|Secondary)', text, re.IGNORECASE)
        if m_front:
            front = int(m_front.group(1))

        return rear, front

    @staticmethod
    def extract_refresh_rate_hz(text: str) -> Optional[int]:
        if not text:
            return None
        m = re.search(r'(\d{2,3})\s*Hz', text, re.IGNORECASE)
        if m:
            return int(m.group(1))
        return None

    @staticmethod
    def extract_display_size(text: str) -> Optional[float]:
        if not text:
            return None
        m = re.search(r'(\d+\.\d+|\d+)\s*(?:inch|inches|cm|\")', text, re.IGNORECASE)
        if m:
            val = float(m.group(1))
            # If in cm, convert to inches
            if "cm" in text.lower() and val > 10.0:
                val = round(val / 2.54, 2)
            if 4.0 <= val <= 8.5:
                return val
        return None
