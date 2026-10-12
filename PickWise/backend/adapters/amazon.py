"""
Amazon adapter module for PickWise.
Extracts product specs using JSON-LD first, then Amazon technical specifications tables and bullets.
"""

import re
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from .base import BaseAdapter

class AmazonAdapter(BaseAdapter):
    site_name = "Amazon"
    domains = ["amazon.in", "amazon.com", "amzn.to", "amzn.in"]

    def parse(self, url: str, html: Optional[str]) -> Dict[str, Any]:
        result = {
            "site": self.site_name,
            "url": url,
            "name": "",
            "brand": "",
            "image": "",
            "specs": {
                "price": None,
                "mrp": None,
                "discount_pct": None,
                "rating": None,
                "review_count": None,
                "ram": None,
                "storage": None,
                "chipset": None,
                "battery_capacity": None,
                "charging_speed": None,
                "rear_camera": None,
                "front_camera": None,
                "display_size": None,
                "refresh_rate": None,
                "display_type": None,
                "os": None
            },
            "status": "success",
            "error": None
        }

        if not html:
            result["status"] = "needs_fallback"
            result["error"] = "Amazon blocked the automated request or timed out. Please input specs manually."
            return result

        soup = BeautifulSoup(html, "html.parser")

        # 1. Try JSON-LD
        json_ld = self.extract_json_ld(soup)
        if json_ld:
            if "name" in json_ld:
                result["name"] = json_ld["name"]
            if "image" in json_ld:
                img = json_ld["image"]
                result["image"] = img[0] if isinstance(img, list) else img
            if "brand" in json_ld:
                brand = json_ld["brand"]
                result["brand"] = brand.get("name", "") if isinstance(brand, dict) else str(brand)
            if "offers" in json_ld:
                offers = json_ld["offers"]
                if isinstance(offers, dict):
                    result["specs"]["price"] = self._to_float(offers.get("price"))
                elif isinstance(offers, list) and offers:
                    result["specs"]["price"] = self._to_float(offers[0].get("price"))
            if "aggregateRating" in json_ld:
                agg = json_ld["aggregateRating"]
                result["specs"]["rating"] = self._to_float(agg.get("ratingValue"))
                result["specs"]["review_count"] = self._to_int(agg.get("reviewCount") or agg.get("ratingCount"))

        # 2. Title from HTML
        if not result["name"]:
            title_el = soup.select_one("#productTitle, #title")
            if title_el:
                result["name"] = title_el.get_text().strip()

        # 3. Price from HTML
        if result["specs"]["price"] is None:
            price_el = soup.select_one("#corePrice_feature_div .a-price .a-offscreen, #corePriceDisplay_desktop_feature_div .a-price .a-offscreen, .a-price .a-offscreen, #priceblock_ourprice")
            if price_el:
                result["specs"]["price"] = self._to_float(price_el.get_text())

        mrp_el = soup.select_one(".a-price.a-text-price .a-offscreen, #basisPrice .a-offscreen, #listPrice")
        if mrp_el:
            result["specs"]["mrp"] = self._to_float(mrp_el.get_text())

        # Discount
        p = result["specs"]["price"]
        mrp = result["specs"]["mrp"]
        if p and mrp and mrp > p:
            result["specs"]["discount_pct"] = round(((mrp - p) / mrp) * 100.0, 1)

        # 4. Rating and reviews
        if result["specs"]["rating"] is None:
            rating_el = soup.select_one("#acrPopover .a-icon-alt, #averageCustomerReviews .a-icon-alt")
            if rating_el:
                # "4.3 out of 5 stars"
                m_r = re.search(r'(\d+\.\d+|\d+)\s*(?:out of|stars)', rating_el.get_text())
                if m_r:
                    result["specs"]["rating"] = float(m_r.group(1))

        if result["specs"]["review_count"] is None:
            rev_el = soup.select_one("#acrCustomerReviewText")
            if rev_el:
                m_rev = re.search(r'([\d,]+)\s*(?:ratings|reviews)', rev_el.get_text(), re.IGNORECASE)
                if m_rev:
                    result["specs"]["review_count"] = self._to_int(m_rev.group(1))

        # 5. Image
        if not result["image"]:
            img_el = soup.select_one("#landingImage, #imgBlkFront, #main-image")
            if img_el and img_el.get("src"):
                result["image"] = img_el["src"]

        # 6. Technical details table
        rows = soup.select("#productDetails_techSpec_section_1 tr, #technicalSpecifications_section_1 tr, #prodDetails tr, .po-row")
        for r in rows:
            th = r.select_one("th, td.a-span3, span.a-text-bold")
            td = r.select_one("td:last-child, span.po-break-word")
            if th and td:
                label = th.get_text().strip().lower()
                val = td.get_text().strip()

                if "ram" in label and not result["specs"]["ram"]:
                    result["specs"]["ram"] = self.extract_ram_gb(val)
                elif ("storage" in label or "memory storage" in label or "rom" in label) and not result["specs"]["storage"]:
                    result["specs"]["storage"] = self.extract_storage_gb(val)
                elif ("processor" in label or "cpu model" in label or "chipset" in label) and not result["specs"]["chipset"]:
                    result["specs"]["chipset"] = val
                elif "battery" in label and not result["specs"]["battery_capacity"]:
                    result["specs"]["battery_capacity"] = self.extract_battery_mah(val)
                elif "screen size" in label and not result["specs"]["display_size"]:
                    result["specs"]["display_size"] = self.extract_display_size(val)
                elif "operating system" in label and not result["specs"]["os"]:
                    result["specs"]["os"] = val

        # 7. Bullets
        bullets = [li.get_text().strip() for li in soup.select("#feature-bullets ul li, #featurebullets_feature_div li")]
        combined_bullets = " | ".join(bullets)
        if combined_bullets:
            if not result["specs"]["ram"]:
                result["specs"]["ram"] = self.extract_ram_gb(combined_bullets)
            if not result["specs"]["storage"]:
                result["specs"]["storage"] = self.extract_storage_gb(combined_bullets)
            if not result["specs"]["battery_capacity"]:
                result["specs"]["battery_capacity"] = self.extract_battery_mah(combined_bullets)
            if not result["specs"]["charging_speed"]:
                result["specs"]["charging_speed"] = self.extract_charging_w(combined_bullets)
            if not result["specs"]["rear_camera"]:
                r_cam, f_cam = self.extract_camera_mp(combined_bullets)
                result["specs"]["rear_camera"] = r_cam
                if f_cam and not result["specs"]["front_camera"]:
                    result["specs"]["front_camera"] = f_cam
            if not result["specs"]["display_size"]:
                result["specs"]["display_size"] = self.extract_display_size(combined_bullets)
            if not result["specs"]["refresh_rate"]:
                result["specs"]["refresh_rate"] = self.extract_refresh_rate_hz(combined_bullets)
            if not result["specs"]["chipset"]:
                m_proc = re.search(r'([A-Za-z0-9\+\-\s]+(?:Processor|Chipset|Bionic))', combined_bullets, re.IGNORECASE)
                if m_proc:
                    result["specs"]["chipset"] = m_proc.group(1).replace("Processor", "").replace("Chipset", "").strip()

        # Check title if ram or storage is still missing
        if not result["specs"]["ram"] and result["name"]:
            result["specs"]["ram"] = self.extract_ram_gb(result["name"])
        if not result["specs"]["storage"] and result["name"]:
            result["specs"]["storage"] = self.extract_storage_gb(result["name"])

        # Display type
        full_text = html.lower()
        if any(term in full_text for term in ["amoled", "super amoled", "oled", "retina"]):
            result["specs"]["display_type"] = "AMOLED"
        elif "ips" in full_text:
            result["specs"]["display_type"] = "IPS LCD"

        # Check if fallback is needed
        if not result["name"] or result["specs"]["price"] is None:
            result["status"] = "needs_fallback"
            result["error"] = "Amazon product specs or price could not be automatically determined. Manual confirmation required."

        return result

    def _to_float(self, val: Any) -> Optional[float]:
        if val is None:
            return None
        try:
            cleaned = str(val).replace(",", "").replace("₹", "").replace("$", "").strip()
            m = re.search(r'\d+(\.\d+)?', cleaned)
            return float(m.group(0)) if m else None
        except Exception:
            return None

    def _to_int(self, val: Any) -> Optional[int]:
        f = self._to_float(val)
        return int(f) if f is not None else None
