# PickWise 📱⚖️

> **Unbiased, Deterministic Product Comparison & Decision Engine for Online Shoppers**

PickWise is a full-stack web application designed to eliminate buyer paralysis. Given 2 to 5 product links from Flipkart or Amazon, PickWise extracts specifications via structured JSON-LD and resilient HTML parsing, scales the hardware metrics through multi-criteria decision mathematics, and delivers a fully traceable verdict with plain-language reasons.

---

## 🚀 Key Features

- **2 to 5 Product Link Comparison**: Compare 2 to 5 links from Flipkart (first) and Amazon (bonus) with real-time validation and deduplication.
- **Priority Presets & Custom Sliders**:
  - `Balanced` (Default): Price 25%, Performance 20%, Camera 15%, Battery 15%, Display 10%, RAM/Storage 10%, Ratings 5%
  - `Gaming`: Heavy emphasis on processor benchmark, display refresh rate, and battery
  - `Camera`: Prioritizes primary rear MP, front selfie sensor, and display
  - `Battery`: Maximizes battery capacity (mAh) and charging speed (W)
  - `Budget`: Maximizes spec-per-rupee value
  - `Custom Sliders`: Fine-tune weights across all 7 evaluation pillars
- **Deterministic Winner Verdict**: No generative LLM hallucinations deciding who wins. Mathematical min-max normalization, 3–4 concrete plain-language reasons, and score out of 100.
- **Close-Call Detection**: If the top two contenders are separated by $\le 3.0$ points, PickWise flags the race as a close call and highlights the deciding trade-off factors rather than declaring a false winner.
- **Category-Wise Champions**: Highlights individual winners for Price, Performance, Camera, Battery, Display, Storage, and Ratings.
- **Side-by-Side Spec Comparison**: Full spec grid with the standout best value in each row highlighted.
- **"Why Not the Others?"**: Contextual rationale explaining why each non-winner fell short.
- **100% Traceability Modal**: "How was this calculated?" reveals raw metric values, normalized scores, weight percentages, and contributed points.
- **40+ Mobile Chipset Benchmark DB**: Snapdragon, Dimensity, Apple A-Series, Google Tensor, and Exynos mapped to calibrated benchmark tiers.
- **Anti-Bot Resilient Manual Fallback**: When e-commerce platforms return 403/500/CAPTCHA challenges, PickWise provides a seamless per-product fallback modal so the user never gets stuck.
- **30-Minute Caching**: In-memory TTL cache prevents duplicate network requests.
- **Responsive & Dark Mode**: Mobile-first design with skeleton loaders, empty state, and one-click demo comparisons.

---

## 🏗️ Architecture & Directory Structure

```
pickwise/
├── backend/
│   ├── app.py                      # Flask API endpoints (/api/compare, /api/extract, /api/presets, /api/chipsets)
│   ├── config.py                   # App configurations, timeouts, cache TTL
│   ├── requirements.txt            # Flask, Flask-Cors, requests, beautifulsoup4, pytest
│   ├── cache/
│   │   └── simple_cache.py         # 30-minute in-memory TTL cache with thread locking
│   ├── categories/                 # Extensible category architecture
│   │   ├── base.py                 # BaseCategory & MetricDefinition
│   │   ├── smartphones.py          # Mobile phone specs, normalizers, Bayesian ratings
│   │   ├── laptops.py              # Laptop category demonstration
│   │   └── data/
│   │       └── chipsets.json       # 40+ common mobile chipsets benchmark DB
│   ├── adapters/                   # Per-site scraper adapters
│   │   ├── base.py                 # BaseAdapter with session headers and JSON-LD extraction
│   │   ├── flipkart.py             # Flipkart adapter (JSON-LD + spec tables + bullet highlights)
│   │   ├── amazon.py               # Amazon adapter (JSON-LD + technical specs table + bullets)
│   │   └── registry.py             # URL validator, deduplicator, router, and cache layer
│   ├── scoring/                    # Deterministic mathematical engine
│   │   ├── engine.py               # Min-max normalization, Bayesian damping, weight redistribution
│   │   ├── reasons.py              # Plain-language reason generator & "Why not the others?"
│   │   └── comparison.py           # Close-call detection & side-by-side spec row tagging
│   └── tests/
│       ├── test_scoring.py         # Tests: ties, missing data, 2 vs 5, close calls, ratings
│       ├── test_adapters.py        # Tests: Flipkart/Amazon parsing, validation, deduplication
│       ├── test_api.py             # Tests: Flask API routes, rate limiting
│       └── verify_real_links.py    # Integration verification script
├── frontend/                       # React 18 + Vite + Tailwind CSS
│   ├── src/
│   │   ├── components/             # Navbar, UrlInputForm, WinnerCard, RankedList,
│   │   │                           # CategoryWinners, SpecComparison, WhyNotOthers,
│   │   │                           # ScoreBreakdown, FallbackModal, LoadingSkeleton, EmptyState
│   │   ├── services/api.js         # API integration client
│   │   ├── App.jsx                 # Master application controller
│   │   └── index.css               # Tailwind CSS styles & animations
│   └── package.json
└── run_servers.ps1                 # Automation script to start backend & frontend
```

---

## ⚙️ Installation & Running the App

### Prerequisites
- Python 3.10+ (tested with Python 3.13 / 3.14)
- Node.js 18+ and npm

### Terminal 1: Start Backend (Port 5000)
```powershell
# Navigate to backend directory
cd C:\Users\hp\.gemini\antigravity\scratch\pickwise

# Install backend dependencies
py -m pip install -r backend/requirements.txt

# Run Flask server
py -m backend.app
```
*Backend API will run at `http://127.0.0.1:5000`*

### Terminal 2: Start Frontend (Port 5173)
```powershell
# Navigate to frontend directory
cd C:\Users\hp\.gemini\antigravity\scratch\pickwise\frontend

# Install dependencies (already installed)
npm install

# Start Vite dev server
npm run dev
```
*Frontend will run at `http://localhost:5173` with automatic API proxying to port 5000.*

---

## 🧪 Running Unit Tests

Run the full pytest suite (19 tests covering scoring, ties, missing data, adapters, and API endpoints):

```powershell
cd C:\Users\hp\.gemini\antigravity\scratch\pickwise
py -m pytest backend/tests
```

To run the real links and fallback integration verification:
```powershell
py backend/tests/verify_real_links.py
```

---

## 🔌 Adding New Site Adapters (e.g., Croma, Reliance Digital)

1. Create a new adapter file in `backend/adapters/croma.py`:
   ```python
   from .base import BaseAdapter

   class CromaAdapter(BaseAdapter):
       site_name = "Croma"
       domains = ["croma.com"]

       def parse(self, url: str, html: Optional[str]) -> Dict[str, Any]:
           # 1. Try structured data: self.extract_json_ld(soup)
           # 2. Extract price, name, and hardware specs using helper regexes:
           #    self.extract_ram_gb(text), self.extract_battery_mah(text), etc.
           # 3. If extraction incomplete, return status="needs_fallback"
   ```
2. Register the adapter in `backend/adapters/registry.py`:
   ```python
   from .croma import CromaAdapter
   self.adapters = [FlipkartAdapter(), AmazonAdapter(), CromaAdapter()]
   ```

---

## 📂 Adding New Product Categories (e.g., Laptops, Smart TVs)

1. Inherit from `BaseCategory` in `backend/categories/<category_name>.py`:
   - Define `groups` (e.g. CPU, GPU, Display, Battery)
   - Define `default_group_weights` and `presets`
   - Define list of `MetricDefinition` objects
2. Register the category in `backend/categories/__init__.py`:
   ```python
   CATEGORIES = {
       "smartphones": SmartphoneCategory,
       "laptops": LaptopCategory,
       "televisions": TelevisionCategory
   }
   ```
The frontend category toggle and scoring engine will automatically inherit the new category's groups and metrics.

---

## 📊 Scoring Engine Math Details

1. **Min-Max Normalization**:
   - For higher-is-better metrics (RAM, Battery, Camera MP, Refresh Rate, Benchmark):
     $$\text{score}(x) = \frac{x - \min(X)}{\max(X) - \min(X)}$$
   - For lower-is-better metrics (Price):
     $$\text{score}(x) = \frac{\max(X) - x}{\max(X) - \min(X)}$$
   *(Tied metrics yield 1.0).*
2. **Bayesian Rating Damping**:
   $$\text{Rating}_{\text{effective}} = \frac{v \cdot R + m \cdot C}{v + m}$$
   where $v = \text{review count}$, $m = 100$, $C = 4.0$ (prior average), $R = \text{star rating}$.
3. **Weight Redistribution**:
   If a product is missing a metric, that metric is dropped for that product, the remaining weights are normalized to sum to 100%, and a confidence score is calculated:
   $$\text{Confidence} = \frac{\sum \text{Present Weights}}{\sum \text{All Weights}} \times 100\%$$
   If confidence drops below 80%, a `Low Confidence` badge is displayed.
