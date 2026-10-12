import React from 'react';
import { HelpCircle, AlertCircle, XCircle } from 'lucide-react';

export default function WhyNotOthers({ whyNotOthers }) {
  if (!whyNotOthers || whyNotOthers.length === 0) return null;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm mb-8 transition">
      <div className="mb-6">
        <div className="flex items-center space-x-2">
          <HelpCircle className="w-5 h-5 text-amber-500" />
          <h3 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">
            Why Not the Others?
          </h3>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Honest, spec-grounded explanations of where each non-winning contender fell short
        </p>
      </div>

      <div className="space-y-3.5">
        {whyNotOthers.map((item) => (
          <div
            key={item.product_id}
            className="p-4 sm:p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
          >
            <div className="flex items-start space-x-3">
              <XCircle className="w-5 h-5 text-rose-500 flex-shrink-0 mt-0.5" />
              <div>
                <div className="flex items-center space-x-2">
                  <h4 className="font-bold text-slate-900 dark:text-white text-sm sm:text-base">
                    {item.name}
                  </h4>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300">
                    Rank #{item.rank}
                  </span>
                </div>
                <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
                  {item.explanation}
                </p>
              </div>
            </div>

            <div className="text-right sm:text-right flex-shrink-0">
              <span className="text-xs font-semibold text-slate-400">
                Score: {item.total_score}/100
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
