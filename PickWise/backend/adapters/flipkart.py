"""
Flipkart adapter module for PickWise.
Extracts product specs using JSON-LD first, then comprehensive HTML tables and highlights.
"""

import re
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from .base import BaseAdapter

class FlipkartAdapter(BaseAdapter):
    site_name = "Flipkart"
    domains = ["flipkart.com", "dl.flipkart.com"]

    def parse(self, url: str, html: Optional[str]) -> Dict[str, Any]:
        """
        Parses Flipkart product page.
        Returns standardized dictionary.
        """
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
            result["error"] = "Unable to fetch content from Flipkart. Please enter specs manually."
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

        # 2. Extract Title / Name from HTML if not in JSON-LD
        if not result["name"]:
            name_el = soup.select_one("span.B_NuCI, h1._6EBuvT, h1.VU-ZEz, h1")
            if name_el:
                result["name"] = name_el.get_text().strip()

        # 3. Extract Price & MRP from HTML
        if result["specs"]["price"] is None:
            price_el = soup.select_one("div.Nx9bqj.CxhGGd, div._30jeq3._16J063, div.Nx9bqj, div._30jeq3")
            if price_el:
                result["specs"]["price"] = self._to_float(price_el.get_text())

        mrp_el = soup.select_one("div.yRaY8j.A6\\+L6v, div._3I9_wc._2p6lfd, div.yRaY8j, div._3I9_wc")
        if mrp_el:
            result["specs"]["mrp"] = self._to_float(mrp_el.get_text())

        # Calculate discount %
        p = result["specs"]["price"]
        mrp = result["specs"]["mrp"]
        if p and mrp and mrp > p:
            result["specs"]["discount_pct"] = round(((mrp - p) / mrp) * 100.0, 1)

        # 4. Extract Rating and Review count from HTML
        if result["specs"]["rating"] is None:
            rating_el = soup.select_one("div.XQDdHH, div._3LWZlK")
            if rating_el:
                result["specs"]["rating"] = self._to_float(rating_el.get_text())

        if result["specs"]["review_count"] is None:
            rev_el = soup.select_one("span.Wphh3N, span._2_R_DZ")
            if rev_el:
                text = rev_el.get_text()
                # e.g. "8,520 Ratings & 920 Reviews"
                m_rev = re.search(r'([\d,]+)\s*(?:Ratings|Reviews)', text)
                if m_rev:
                    result["specs"]["review_count"] = self._to_int(m_rev.group(1))

        # 5. Extract Image if missing
        if not result["image"]:
            img_el = soup.select_one("img._396cs4, img.DByuf4, img._2r_T1I")
            if img_el and img_el.get("src"):
                result["image"] = img_el["src"]

        # 6. Extract Specifications from Flipkart Spec Table
        # Flipkart specs table rows: title in td/col 1, value in td/col 2
        spec_text_corpus = []
        table_rows = soup.select("tr.W_R1IK, table._14cfVK tr, div._1UhVsV tr")
        for row in table_rows:
            cols = row.select("td")
            if len(cols) >= 2:
                label = cols[0].get_text().strip().lower()
                val = cols[1].get_text().strip()
                spec_text_corpus.append(f"{label}: {val}")

                if "ram" in label and not result["specs"]["ram"]:
                    result["specs"]["ram"] = self.extract_ram_gb(val)
                elif "storage" in label and not result["specs"]["storage"]:
                    result["specs"]["storage"] = self.extract_storage_gb(val)
                elif ("processor type" in label or "processor brand" in label) and not result["specs"]["chipset"]:
                    result["specs"]["chipset"] = val
                elif "battery capacity" in label and not result["specs"]["battery_capacity"]:
                    result["specs"]["battery_capacity"] = self.extract_battery_mah(val)
                elif "primary camera" in label and not result["specs"]["rear_camera"]:
                    r, _ = self.extract_camera_mp(val)
                    result["specs"]["rear_camera"] = r
                elif "secondary camera" in label and not result["specs"]["front_camera"]:
                    _, f = self.extract_camera_mp(val)
                    result["specs"]["front_camera"] = f or self.extract_front_camera_fallback(val)
                elif "display size" in label and not result["specs"]["display_size"]:
                    result["specs"]["display_size"] = self.extract_display_size(val)
                elif "refresh rate" in label and not result["specs"]["refresh_rate"]:
                    result["specs"]["refresh_rate"] = self.extract_refresh_rate_hz(val)
                elif "operating system" in label and not result["specs"]["os"]:
                    result["specs"]["os"] = val

        # 7. Extract from Highlights Bullet List
        highlight_items = [li.get_text().strip() for li in soup.select("div._241R88 ul li, div._21AqiJ ul li, li._21AqiJ, div._3k-BhJ li")]
        combined_highlights = " | ".join(highlight_items)

        if combined_highlights:
            if not result["specs"]["ram"]:
                result["specs"]["ram"] = self.extract_ram_gb(combined_highlights)
            if not result["specs"]["storage"]:
                result["specs"]["storage"] = self.extract_storage_gb(combined_highlights)
            if not result["specs"]["battery_capacity"]:
                result["specs"]["battery_capacity"] = self.extract_battery_mah(combined_highlights)
            if not result["specs"]["charging_speed"]:
                result["specs"]["charging_speed"] = self.extract_charging_w(combined_highlights)
            if not result["specs"]["rear_camera"]:
                r, f = self.extract_camera_mp(combined_highlights)
                result["specs"]["rear_camera"] = r
                if f and not result["specs"]["front_camera"]:
                    result["specs"]["front_camera"] = f
            if not result["specs"]["display_size"]:
                result["specs"]["display_size"] = self.extract_display_size(combined_highlights)
            if not result["specs"]["refresh_rate"]:
                result["specs"]["refresh_rate"] = self.extract_refresh_rate_hz(combined_highlights)
            if not result["specs"]["chipset"]:
                # Check highlights for processor mentions
                m_proc = re.search(r'([A-Za-z0-9\+\-\s]+(?:Processor|Chipset|Bionic))', combined_highlights, re.IGNORECASE)
                if m_proc:
                    result["specs"]["chipset"] = m_proc.group(1).replace("Processor", "").replace("Chipset", "").strip()

        # Check title if ram or storage is still missing
        if not result["specs"]["ram"] and result["name"]:
            result["specs"]["ram"] = self.extract_ram_gb(result["name"])
        if not result["specs"]["storage"] and result["name"]:
            result["specs"]["storage"] = self.extract_storage_gb(result["name"])

        # Extract display type (AMOLED / OLED / LCD)
        full_text = html.lower()
        if any(term in full_text for term in ["amoled", "super amoled", "oled", "retina"]):
            result["specs"]["display_type"] = "AMOLED"
        elif "ips" in full_text:
            result["specs"]["display_type"] = "IPS LCD"
        elif "lcd" in full_text:
            result["specs"]["display_type"] = "LCD"

        # Check if enough data was extracted
        # If critical fields (name, price) are completely missing, mark as needs_fallback
        if not result["name"] or result["specs"]["price"] is None:
            result["status"] = "needs_fallback"
            result["error"] = "Could not automatically extract product title or price. Please confirm details below."

        return result

    def extract_front_camera_fallback(self, text: str) -> Optional[int]:
        m = re.search(r'(\d{1,3})\s*MP', text, re.IGNORECASE)
        return int(m.group(1)) if m else None

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
