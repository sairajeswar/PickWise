import React from 'react';
import { Sparkles, Shield, Cpu, SlidersHorizontal, ArrowRight } from 'lucide-react';

export default function EmptyState({ onSelectDemo }) {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-3xl p-8 sm:p-12 border border-slate-200 dark:border-slate-800 text-center shadow-sm">
      <div className="max-w-xl mx-auto space-y-6">
        
        <div className="inline-flex p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400">
          <Sparkles className="w-8 h-8" />
        </div>

        <div className="space-y-2">
          <h3 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            Stop Guessing. Decide with Precision.
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
            PickWise uses normalized min-max math, verified hardware benchmarks, and Bayesian community rating models to find your optimal gadget.
          </p>
        </div>

        {/* 3 Pillars */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 text-left">
          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
            <Cpu className="w-5 h-5 text-emerald-500 mb-2" />
            <h4 className="font-bold text-xs text-slate-900 dark:text-white">40+ Chipset Benchmarks</h4>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
              Snapdragon, Dimensity, Apple & Tensor matched to calibrated tiers.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
            <SlidersHorizontal className="w-5 h-5 text-emerald-500 mb-2" />
            <h4 className="font-bold text-xs text-slate-900 dark:text-white">Adaptive Presets</h4>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
              Balanced, Gaming, Camera, Battery, or Budget weight sliders.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
            <Shield className="w-5 h-5 text-emerald-500 mb-2" />
            <h4 className="font-bold text-xs text-slate-900 dark:text-white">100% Traceable</h4>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
              Every score point is backed by formula math, never AI bias.
            </p>
          </div>
        </div>

        {/* 1-click sample button */}
        <div className="pt-2">
          <button
            onClick={onSelectDemo}
            className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold text-xs text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/60 hover:bg-emerald-100 dark:hover:bg-emerald-900 border border-emerald-200 dark:border-emerald-800 transition"
          >
            <span>Try 3-Way Midrange Showdown (1-Click Demo)</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  );
}
