import React from 'react';

export default function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Winner card skeleton */}
      <div className="h-64 bg-slate-200 dark:bg-slate-800 rounded-3xl" />
      
      {/* Ranked list skeleton */}
      <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 space-y-4">
        <div className="h-6 w-48 bg-slate-200 dark:bg-slate-800 rounded-lg" />
        <div className="h-20 bg-slate-100 dark:bg-slate-800/60 rounded-2xl" />
        <div className="h-20 bg-slate-100 dark:bg-slate-800/60 rounded-2xl" />
        <div className="h-20 bg-slate-100 dark:bg-slate-800/60 rounded-2xl" />
      </div>

      {/* Grid skeleton */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="h-28 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
        <div className="h-28 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
        <div className="h-28 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
        <div className="h-28 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
      </div>
    </div>
  );
}
