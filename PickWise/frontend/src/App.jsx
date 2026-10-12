import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import UrlInputForm from './components/UrlInputForm';
import WinnerCard from './components/WinnerCard';
import RankedList from './components/RankedList';
import CategoryWinners from './components/CategoryWinners';
import SpecComparison from './components/SpecComparison';
import WhyNotOthers from './components/WhyNotOthers';
import ScoreBreakdown from './components/ScoreBreakdown';
import FallbackModal from './components/FallbackModal';
import LoadingSkeleton from './components/LoadingSkeleton';
import EmptyState from './components/EmptyState';
import { fetchPresets, fetchChipsets, extractProducts, compareProducts } from './services/api';

const SAMPLE_DEMO_LINKS = [
  'https://www.flipkart.com/oneplus-12r-cool-blue-256-gb/p/itm7e793d5a42861',
  'https://www.amazon.in/dp/B0CX123ABC-iqoo-neo-9-pro',
  'https://www.flipkart.com/redmi-note-13-pro-5g-coral-purple-128-gb/p/itm50febe330d200'
];

const SAMPLE_DEMO_PRODUCTS = [
  {
    id: 'sample-oneplus-12r',
    name: 'OnePlus 12R 5G (Cool Blue, 256 GB)',
    brand: 'OnePlus',
    url: 'https://www.flipkart.com/oneplus-12r',
    specs: {
      price: 39999,
      mrp: 42999,
      discount_pct: 7,
      rating: 4.5,
      review_count: 9400,
      ram: 16,
      storage: 256,
      chipset: 'Snapdragon 8 Gen 2',
      battery_capacity: 5500,
      charging_speed: 100,
      rear_camera: 50,
      front_camera: 16,
      display_size: 6.78,
      refresh_rate: 120,
      display_type: 'AMOLED',
      os: 'OxygenOS (Android 14)'
    }
  },
  {
    id: 'sample-iqoo-neo-9-pro',
    name: 'iQOO Neo 9 Pro 5G (Fiery Red, 128 GB)',
    brand: 'iQOO',
    url: 'https://www.amazon.in/iqoo-neo-9-pro',
    specs: {
      price: 34999,
      mrp: 39999,
      discount_pct: 12,
      rating: 4.4,
      review_count: 14200,
      ram: 8,
      storage: 128,
      chipset: 'Snapdragon 8 Gen 2',
      battery_capacity: 5160,
      charging_speed: 120,
      rear_camera: 50,
      front_camera: 16,
      display_size: 6.78,
      refresh_rate: 144,
      display_type: 'LTPO AMOLED',
      os: 'Funtouch OS 14 (Android 14)'
    }
  },
  {
    id: 'sample-redmi-note-13-pro-plus',
    name: 'Redmi Note 13 Pro+ 5G (Fusion White, 256 GB)',
    brand: 'Redmi',
    url: 'https://www.flipkart.com/redmi-note-13-pro-plus',
    specs: {
      price: 29999,
      mrp: 33999,
      discount_pct: 11,
      rating: 4.3,
      review_count: 18500,
      ram: 8,
      storage: 256,
      chipset: 'Dimensity 7200-Ultra',
      battery_capacity: 5000,
      charging_speed: 120,
      rear_camera: 200,
      front_camera: 16,
      display_size: 6.67,
      refresh_rate: 120,
      display_type: 'Curved AMOLED',
      os: 'MIUI 14 (Android 13)'
    }
  }
];

export default function App() {
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('pickwise-theme') === 'dark' ||
      (!('pickwise-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
  });

  const [selectedCategory, setSelectedCategory] = useState('smartphones');
  const [urls, setUrls] = useState([
    'https://www.flipkart.com/oneplus-12r-cool-blue-256-gb/p/itm7e793d5a42861',
    'https://www.flipkart.com/redmi-note-13-pro-5g-coral-purple-128-gb/p/itm50febe330d200'
  ]);
  const [presets, setPresets] = useState({});
  const [selectedPreset, setSelectedPreset] = useState('Balanced');
  const [weights, setWeights] = useState({});
  const [groupLabels, setGroupLabels] = useState({});
  const [chipsets, setChipsets] = useState([]);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [comparisonResult, setComparisonResult] = useState(null);

  // Fallback modal & editing state
  const [fallbackProduct, setFallbackProduct] = useState(null);
  const [pendingExtractedProducts, setPendingExtractedProducts] = useState(null);

  // Traceability modal
  const [traceabilityProductId, setTraceabilityProductId] = useState(null);

  // Sync dark mode class
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('pickwise-theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('pickwise-theme', 'light');
    }
  }, [darkMode]);

  // Load category presets and chipsets on mount
  useEffect(() => {
    async function loadInitialData() {
      try {
        const presetData = await fetchPresets(selectedCategory);
        setPresets(presetData.presets || {});
        setWeights(presetData.default_weights || {});
        setGroupLabels(presetData.groups || {});
        setSelectedPreset('Balanced');

        const chipData = await fetchChipsets();
        setChipsets(chipData.chipsets || []);
      } catch (err) {
        console.error('Initial data load error:', err);
      }
    }
    loadInitialData();
  }, [selectedCategory]);

  // Load sample demo battle
  const handleSelectDemo = async () => {
    setError(null);
    setUrls(SAMPLE_DEMO_LINKS);
    setIsLoading(true);
    try {
      const compRes = await compareProducts({
        products: SAMPLE_DEMO_PRODUCTS,
        weights,
        category: selectedCategory
      });
      setComparisonResult(compRes);
    } catch (err) {
      setError(err.message || 'Failed to calculate sample demo');
    } finally {
      setIsLoading(false);
    }
  };

  // Main Submit Handler
  const handleStartFilter = async () => {
    setError(null);

    // 1. Client-side URL count check (min 2, max 5)
    const validUrls = urls.map(u => u.trim()).filter(Boolean);
    if (validUrls.length < 2) {
      setError('Please provide at least 2 product links to begin comparison.');
      return;
    }
    if (validUrls.length > 5) {
      setError('You can compare a maximum of 5 product links at a time.');
      return;
    }

    // 2. Duplicate check
    const lowerUrls = validUrls.map(u => u.toLowerCase().split('?')[0]);
    const uniqueUrls = new Set(lowerUrls);
    if (uniqueUrls.size !== lowerUrls.length) {
      setError('Duplicate links detected. Please ensure all product links are distinct.');
      return;
    }

    // 3. Invalid protocol / domain check
    for (let i = 0; i < validUrls.length; i++) {
      const u = validUrls[i];
      if (!u.startsWith('http://') && !u.startsWith('https://')) {
        setError(`Link #${i + 1} is invalid. It must start with http:// or https://`);
        return;
      }
      if (!u.includes('flipkart.com') && !u.includes('amazon.in') && !u.includes('amazon.com') && !u.includes('amzn.')) {
        setError(`Link #${i + 1} is not from a supported store. Currently Flipkart and Amazon links are supported.`);
        return;
      }
    }

    setIsLoading(true);

    try {
      // Step A: Extract products from links
      const extractRes = await extractProducts(validUrls);
      const extractedList = extractRes.products || [];

      // Check if any product failed extraction and needs manual fallback
      const needy = extractedList.find(p => p.status === 'needs_fallback');
      if (needy) {
        setPendingExtractedProducts(extractedList);
        setFallbackProduct(needy);
        setIsLoading(false);
        return;
      }

      // Step B: If all succeeded, proceed directly to compare
      const compRes = await compareProducts({
        products: extractedList,
        weights,
        category: selectedCategory
      });
      setComparisonResult(compRes);

    } catch (err) {
      setError(err.message || 'An error occurred during product analysis. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Fallback modal save handler
  const handleSaveFallbackProduct = async (updatedProduct) => {
    setFallbackProduct(null);

    let productList = [];
    if (pendingExtractedProducts) {
      productList = pendingExtractedProducts.map(p =>
        (p.id === updatedProduct.id || p.url === updatedProduct.url) ? updatedProduct : p
      );
    } else if (comparisonResult?.ranked_products) {
      productList = comparisonResult.ranked_products.map(p =>
        (p.product_id === updatedProduct.id || p.id === updatedProduct.id) ? updatedProduct : p
      );
    } else {
      productList = [updatedProduct];
    }

    // Check if another product still needs fallback
    const nextNeedy = productList.find(p => p.status === 'needs_fallback');
    if (nextNeedy) {
      setPendingExtractedProducts(productList);
      setFallbackProduct(nextNeedy);
      return;
    }

    // Run comparison with updated products
    setIsLoading(true);
    setPendingExtractedProducts(null);
    try {
      const compRes = await compareProducts({
        products: productList,
        weights,
        category: selectedCategory
      });
      setComparisonResult(compRes);
    } catch (err) {
      setError(err.message || 'Failed to compute scores with manual specs');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col transition-colors duration-200">
      
      {/* Navbar */}
      <Navbar
        darkMode={darkMode}
        setDarkMode={setDarkMode}
        onSelectDemo={handleSelectDemo}
        selectedCategory={selectedCategory}
        setSelectedCategory={setSelectedCategory}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8">
        
        {/* Input Form Card */}
        <UrlInputForm
          urls={urls}
          setUrls={setUrls}
          presets={presets}
          selectedPreset={selectedPreset}
          setSelectedPreset={setSelectedPreset}
          weights={weights}
          setWeights={setWeights}
          groupLabels={groupLabels}
          onSubmit={handleStartFilter}
          isLoading={isLoading}
          error={error}
          setError={setError}
        />

        {/* Loading Skeleton */}
        {isLoading && <LoadingSkeleton />}

        {/* Results Presentation */}
        {!isLoading && comparisonResult && (
          <div className="space-y-8 transition animate-fade-in">
            
            {/* 1. Winner Card */}
            <WinnerCard
              winner={comparisonResult.winner}
              closeCall={comparisonResult.close_call}
              onOpenTraceability={(prodId) => setTraceabilityProductId(prodId)}
            />

            {/* 2. Ranked List */}
            <RankedList
              rankedProducts={comparisonResult.ranked_products}
              onOpenTraceability={(prodId) => setTraceabilityProductId(prodId)}
              onEditProduct={(prod) => setFallbackProduct(prod)}
            />

            {/* 3. Category-wise Winners */}
            <CategoryWinners
              categoryWinners={comparisonResult.category_winners}
            />

            {/* 4. Side-by-Side Spec Comparison */}
            <SpecComparison
              tableRows={comparisonResult.spec_comparison_table}
              rankedProducts={comparisonResult.ranked_products}
            />

            {/* 5. Why Not The Others? */}
            <WhyNotOthers
              whyNotOthers={comparisonResult.why_not_others}
            />

          </div>
        )}

        {/* Empty State when no results and not loading */}
        {!isLoading && !comparisonResult && (
          <EmptyState onSelectDemo={handleSelectDemo} />
        )}

      </main>

      {/* Fallback & Edit Modal */}
      {fallbackProduct && (
        <FallbackModal
          product={fallbackProduct}
          chipsets={chipsets}
          onSave={handleSaveFallbackProduct}
          onClose={() => setFallbackProduct(null)}
        />
      )}

      {/* Traceable Score Breakdown Modal */}
      {traceabilityProductId && comparisonResult && (
        <ScoreBreakdown
          isOpen={Boolean(traceabilityProductId)}
          onClose={() => setTraceabilityProductId(null)}
          rankedProducts={comparisonResult.ranked_products}
          initialProductId={traceabilityProductId}
          appliedWeights={comparisonResult.applied_weights}
        />
      )}

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-slate-800 py-6 text-center text-xs text-slate-500 dark:text-slate-400">
        <p>
          PickWise &bull; Deterministic Multi-Criteria Decision Analysis &bull; Flipkart & Amazon India
        </p>
      </footer>

    </div>
  );
}
