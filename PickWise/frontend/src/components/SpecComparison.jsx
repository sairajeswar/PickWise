import React from 'react';
import { Columns, Check, Star } from 'lucide-react';

export default function SpecComparison({
  tableRows,
  rankedProducts
}) {
  if (!tableRows || tableRows.length === 0 || !rankedProducts) return null;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm mb-8 transition">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
        <div>
          <div className="flex items-center space-x-2">
            <Columns className="w-5 h-5 text-emerald-500" />
            <h3 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">
              Side-by-Side Spec Comparison
            </h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Highlighted green badges indicate the standout best value in each specification row
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs text-slate-500">
          <span className="w-3 h-3 rounded bg-emerald-500/20 border border-emerald-500/40 inline-block" />
          <span>= Best in test</span>
        </div>
      </div>

      {/* Table Container */}
      <div className="overflow-x-auto rounded-2xl border border-slate-200 dark:border-slate-800">
        <table className="w-full text-left text-sm border-collapse">
          <thead>
            <tr className="bg-slate-50 dark:bg-slate-800/70 border-b border-slate-200 dark:border-slate-800">
              <th className="p-4 font-bold text-slate-700 dark:text-slate-300 min-w-[160px] sticky left-0 bg-slate-50 dark:bg-slate-850 z-10 shadow-[2px_0_5px_rgba(0,0,0,0.03)]">
                Specification
              </th>
              {rankedProducts.map((p) => (
                <th key={p.product_id} className="p-4 font-bold text-slate-900 dark:text-white min-w-[200px] max-w-[240px]">
                  <div className="flex items-center space-x-1.5 mb-1">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                      #{p.rank}
                    </span>
                    <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400">
                      {p.total_score} pts
                    </span>
                  </div>
                  <div className="text-sm truncate font-bold text-slate-900 dark:text-white" title={p.name}>
                    {p.name}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
            {tableRows.map((row) => (
              <tr key={row.key} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition">
                <td className="p-4 font-semibold text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider sticky left-0 bg-white dark:bg-slate-900 z-10 shadow-[2px_0_5px_rgba(0,0,0,0.03)]">
                  {row.label}
                </td>
                {row.cells.map((cell) => {
                  const isBest = cell.is_best;
                  return (
                    <td
                      key={cell.product_id}
                      className={`p-4 transition ${
                        isBest
                          ? 'bg-emerald-500/10 dark:bg-emerald-500/15 font-semibold text-emerald-950 dark:text-emerald-200'
                          : 'text-slate-700 dark:text-slate-300'
                      }`}
                    >
                      <div className="flex items-center justify-between space-x-2">
                        <span>{cell.display_text}</span>
                        {isBest && (
                          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-emerald-500 text-white shadow-sm flex-shrink-0">
                            Best
                          </span>
                        )}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}
