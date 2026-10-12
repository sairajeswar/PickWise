import React from 'react';
import { Trophy, CheckCircle2, AlertTriangle, HelpCircle, ArrowRight } from 'lucide-react';

export default function WinnerCard({
  winner,
  closeCall,
  onOpenTraceability
}) {
  if (!winner) return null;

  return (
    <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-500 via-emerald-600 to-teal-700 p-1 shadow-xl shadow-emerald-900/10 mb-8 text-white transition">
      
      {/* Background decoration */}
      <div className="absolute -right-16 -top-16 w-64 h-64 bg-white/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute right-12 bottom-4 opacity-10 pointer-events-none">
        <Trophy className="w-56 h-56" />
      </div>

      <div className="relative bg-emerald-950/20 backdrop-blur-sm rounded-[22px] p-6 sm:p-8">
        
        {/* Close Call Banner */}
        {closeCall?.is_close_call && (
          <div className="mb-6 p-4 rounded-2xl bg-amber-500/20 border border-amber-300/30 text-amber-100 flex items-start space-x-3 backdrop-blur-md">
            <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5 text-amber-300" />
            <div>
              <span className="font-bold text-amber-200">Very close match! ({closeCall.score_difference} pts difference)</span>
              <p className="text-xs sm:text-sm mt-0.5 text-amber-100/90 leading-relaxed">
                {closeCall.recommendation}
              </p>
            </div>
          </div>
        )}

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          
          {/* Main Info */}
          <div className="space-y-4 max-w-2xl">
            <div className="flex items-center space-x-3">
              <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-white/20 text-emerald-100 text-xs font-semibold uppercase tracking-wider backdrop-blur-sm">
                <Trophy className="w-3.5 h-3.5 text-amber-300 fill-amber-300" />
                <span>Overall Winner</span>
              </span>

              {winner.is_low_confidence ? (
                <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full bg-amber-500/30 text-amber-200 text-xs font-medium">
                  <AlertTriangle className="w-3 h-3" />
                  <span>Low Confidence ({winner.confidence_pct}%)</span>
                </span>
              ) : (
                <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full bg-emerald-400/20 text-emerald-200 text-xs font-medium">
                  <span>High Confidence ({winner.confidence_pct}%)</span>
                </span>
              )}
            </div>

            <div>
              <p className="text-emerald-200 text-sm font-medium">Best choice for your priorities</p>
              <h3 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white mt-1">
                {winner.name}
              </h3>
            </div>

            {/* Reasons Bullets */}
            <div className="space-y-2.5 pt-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-emerald-200/90">
                Key Decision Reasons:
              </p>
              <ul className="space-y-2">
                {winner.reasons?.map((reason, idx) => (
                  <li key={idx} className="flex items-start space-x-2.5 text-sm sm:text-base text-emerald-50">
                    <CheckCircle2 className="w-5 h-5 flex-shrink-0 text-emerald-300 mt-0.5" />
                    <span className="leading-snug">{reason}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Score Badge & Traceability Trigger */}
          <div className="flex flex-col items-center justify-center p-6 bg-white/10 rounded-2xl border border-white/20 backdrop-blur-md text-center min-w-[200px] flex-shrink-0">
            <span className="text-xs uppercase tracking-wider font-semibold text-emerald-200">
              PickWise Score
            </span>
            <div className="flex items-baseline space-x-1 my-1">
              <span className="text-5xl sm:text-6xl font-black text-white tracking-tight">
                {winner.total_score}
              </span>
              <span className="text-emerald-200 font-medium text-lg">/100</span>
            </div>
            
            <button
              onClick={() => onOpenTraceability(winner.product_id)}
              className="mt-4 flex items-center space-x-1 text-xs font-medium px-3 py-1.5 rounded-lg bg-white/20 hover:bg-white/30 text-white transition"
            >
              <HelpCircle className="w-3.5 h-3.5" />
              <span>How was this calculated?</span>
            </button>
          </div>

        </div>

      </div>
    </div>
  );
}
