import React, { useState } from 'react';
import { X, Calculator, Info, ShieldCheck, AlertCircle } from 'lucide-react';

export default function ScoreBreakdown({
  isOpen,
  onClose,
  rankedProducts,
  initialProductId,
  appliedWeights
}) {
  const [selectedProductId, setSelectedProductId] = useState(initialProductId || rankedProducts?.[0]?.product_id);

  if (!isOpen || !rankedProducts || rankedProducts.length === 0) return null;

  const currentProduct = rankedProducts.find(p => p.product_id === selectedProductId) || rankedProducts[0];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm overflow-y-auto">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl transition">
        
        {/* Header */}
        <div className="p-6 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
              <Calculator className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white">
                How Was This Calculated?
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                100% deterministic mathematical traceability &bull; No LLM hallucinated scoring
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Product selector tabs */}
        <div className="px-6 pt-4 pb-2 border-b border-slate-200 dark:border-slate-800 overflow-x-auto flex space-x-2">
          {rankedProducts.map((p) => (
            <button
              key={p.product_id}
              onClick={() => setSelectedProductId(p.product_id)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition flex items-center space-x-1.5 ${
                p.product_id === currentProduct.product_id
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
              }`}
            >
              <span>#{p.rank}</span>
              <span className="truncate max-w-[120px]">{p.name}</span>
              <span className="opacity-80">({p.total_score} pts)</span>
            </button>
          ))}
        </div>

        {/* Body Content */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-sm text-slate-700 dark:text-slate-300">
          
          {/* Methodology Info Box */}
          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 space-y-2 text-xs text-slate-600 dark:text-slate-400">
            <div className="flex items-center space-x-1.5 font-bold text-slate-900 dark:text-slate-100">
              <Info className="w-4 h-4 text-emerald-500" />
              <span>Mathematical Formulation</span>
            </div>
            <ul className="list-disc list-inside space-y-1">
              <li><strong>Min-Max Scaling:</strong> Scaled across only the {rankedProducts.length} compared products. For price, lower scores higher: <code className="px-1 bg-slate-200 dark:bg-slate-700 rounded">(max - price) / (max - min)</code>.</li>
              <li><strong>Bayesian Damped Ratings:</strong> Review counts weight the score with a prior of 4.0 and 100 review threshold so low-sample 5.0 ratings don't skew results.</li>
              <li><strong>Missing Spec Redistribution:</strong> If a specification is unavailable, its weight is redistributed across present metrics and the product receives a confidence rating of {currentProduct.confidence_pct}%.</li>
            </ul>
          </div>

          {/* Missing metrics banner if any */}
          {currentProduct.missing_metrics?.length > 0 && (
            <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/40 text-xs text-amber-800 dark:text-amber-300 flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <div>
                <strong>Missing Specs ({currentProduct.missing_metrics.length}): </strong>
                {currentProduct.missing_metrics.map(m => m.name).join(', ')}. 
                Weights were automatically redistributed to present metrics.
              </div>
            </div>
          )}

          {/* Detailed Metric Table */}
          <div className="rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 dark:bg-slate-800 font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                <tr>
                  <th className="p-3">Metric</th>
                  <th className="p-3">Raw Value</th>
                  <th className="p-3">Batch Range</th>
                  <th className="p-3">Norm Score</th>
                  <th className="p-3">Weight</th>
                  <th className="p-3 text-right">Points Earned</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                {currentProduct.metric_breakdowns?.map((m) => (
                  <tr key={m.key} className="hover:bg-slate-50 dark:hover:bg-slate-800/30">
                    <td className="p-3 font-semibold text-slate-900 dark:text-white">
                      {m.name}
                    </td>
                    <td className="p-3">
                      {m.raw_value} {m.unit}
                    </td>
                    <td className="p-3 text-slate-500">
                      [{m.min_batch} – {m.max_batch}]
                    </td>
                    <td className="p-3 font-mono text-emerald-600 dark:text-emerald-400 font-semibold">
                      {(m.norm_score * 100).toFixed(1)}%
                    </td>
                    <td className="p-3 text-slate-500">
                      {m.weight}%
                    </td>
                    <td className="p-3 text-right font-bold text-slate-900 dark:text-white">
                      +{m.points_earned} pts
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot className="bg-slate-100 dark:bg-slate-800 font-bold text-slate-900 dark:text-white">
                <tr>
                  <td colSpan={5} className="p-3 text-right">
                    Final Scaled Total Score:
                  </td>
                  <td className="p-3 text-right text-emerald-600 dark:text-emerald-400 text-sm">
                    {currentProduct.total_score} / 100
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>

        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 dark:border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-slate-900 dark:bg-slate-800 hover:bg-slate-800 dark:hover:bg-slate-700"
          >
            Close Breakdown
          </button>
        </div>

      </div>
    </div>
  );
}
