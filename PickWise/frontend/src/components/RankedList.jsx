import React from 'react';
import { Medal, HelpCircle, AlertCircle, Edit3, ExternalLink } from 'lucide-react';

const RANK_BADGES = {
  1: { bg: 'bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border-amber-300 dark:border-amber-700', label: '1st' },
  2: { bg: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-600', label: '2nd' },
  3: { bg: 'bg-amber-900/10 dark:bg-amber-900/30 text-amber-900 dark:text-amber-200 border-amber-800/30', label: '3rd' },
  4: { bg: 'bg-slate-100 dark:bg-slate-800 text-slate-500 border-slate-200 dark:border-slate-700', label: '4th' },
  5: { bg: 'bg-slate-100 dark:bg-slate-800 text-slate-500 border-slate-200 dark:border-slate-700', label: '5th' },
};

export default function RankedList({
  rankedProducts,
  onOpenTraceability,
  onEditProduct
}) {
  if (!rankedProducts || rankedProducts.length === 0) return null;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm mb-8 transition">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">
            Ranked Leaderboard
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Normalized composite scores scaled from 0 to 100 based on your priorities
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {rankedProducts.map((product) => {
          const badge = RANK_BADGES[product.rank] || RANK_BADGES[5];
          const price = product.specs?.price ? `₹${parseInt(product.specs.price).toLocaleString()}` : 'Price unlisted';
          const chip = product.matched_chipset || product.specs?.chipset || 'Processor N/A';

          return (
            <div
              key={product.product_id}
              className={`p-4 sm:p-5 rounded-2xl border transition-all ${
                product.rank === 1
                  ? 'border-emerald-300 dark:border-emerald-700/60 bg-emerald-50/30 dark:bg-emerald-950/20'
                  : 'border-slate-200 dark:border-slate-800 bg-slate-50/40 dark:bg-slate-800/30 hover:border-slate-300 dark:hover:border-slate-700'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                
                {/* Left: Rank & Title */}
                <div className="flex items-start space-x-3.5 flex-1 min-w-0">
                  <span className={`w-9 h-9 rounded-xl border flex items-center justify-center font-bold text-xs flex-shrink-0 ${badge.bg}`}>
                    {badge.label}
                  </span>
                  
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center space-x-2 flex-wrap">
                      <h4 className="font-bold text-slate-900 dark:text-white text-base truncate">
                        {product.name}
                      </h4>
                      {product.url && (
                        <a
                          href={product.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-slate-400 hover:text-emerald-500 transition"
                          title="View on store"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      )}
                    </div>

                    <div className="flex items-center space-x-3 text-xs text-slate-500 dark:text-slate-400 mt-1 flex-wrap">
                      <span className="font-semibold text-slate-800 dark:text-slate-200">{price}</span>
                      <span>&bull;</span>
                      <span>{chip}</span>
                      {product.chipset_approximate && (
                        <span className="text-[10px] text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 px-1.5 py-0.2 rounded border border-amber-200 dark:border-amber-800">
                          approx.
                        </span>
                      )}
                      {product.is_low_confidence && (
                        <>
                          <span>&bull;</span>
                          <span className="flex items-center space-x-1 text-amber-600 dark:text-amber-400 font-medium">
                            <AlertCircle className="w-3 h-3" />
                            <span>Low confidence ({product.confidence_pct}%)</span>
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                {/* Right: Score & Actions */}
                <div className="flex items-center justify-between sm:justify-end space-x-4 flex-shrink-0">
                  <div className="text-right">
                    <div className="flex items-baseline justify-end space-x-1">
                      <span className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
                        {product.total_score}
                      </span>
                      <span className="text-xs text-slate-400">/100</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => onEditProduct(product)}
                      className="p-2 rounded-xl text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                      title="Edit specifications"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => onOpenTraceability(product.product_id)}
                      className="p-2 rounded-xl text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                      title="Inspect calculation details"
                    >
                      <HelpCircle className="w-4 h-4" />
                    </button>
                  </div>
                </div>

              </div>

              {/* Progress Bar */}
              <div className="mt-3.5 w-full bg-slate-200 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${
                    product.rank === 1
                      ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                      : 'bg-emerald-600/70 dark:bg-emerald-500/60'
                  }`}
                  style={{ width: `${Math.min(Math.max(product.total_score, 5), 100)}%` }}
                />
              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
}
