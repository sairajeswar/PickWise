import React from 'react';
import { Tag, Cpu, Camera, BatteryCharging, Monitor, HardDrive, Star, Award } from 'lucide-react';

const CATEGORY_ICONS = {
  price: Tag,
  performance: Cpu,
  camera: Camera,
  battery: BatteryCharging,
  display: Monitor,
  storage: HardDrive,
  ratings: Star
};

export default function CategoryWinners({ categoryWinners }) {
  if (!categoryWinners || categoryWinners.length === 0) return null;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm mb-8 transition">
      <div className="mb-6">
        <div className="flex items-center space-x-2">
          <Award className="w-5 h-5 text-emerald-500" />
          <h3 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">
            Category-Wise Champions
          </h3>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Who takes the crown in each specific evaluation pillar
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {categoryWinners.map((item) => {
          const Icon = CATEGORY_ICONS[item.group_key] || Award;
          return (
            <div
              key={item.group_key}
              className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 flex flex-col justify-between hover:border-emerald-300 dark:hover:border-emerald-700/50 transition group"
            >
              <div>
                <div className="flex items-center justify-between mb-2.5">
                  <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 flex items-center space-x-1.5">
                    <Icon className="w-4 h-4 text-emerald-500" />
                    <span>{item.group_name}</span>
                  </span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                    {Math.round(item.winner_score)}% score
                  </span>
                </div>

                <h4 className="font-bold text-slate-900 dark:text-white text-sm line-clamp-1 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition">
                  {item.winner_name}
                </h4>
              </div>

              <div className="mt-3 pt-2.5 border-t border-slate-200/60 dark:border-slate-700/60 flex items-center justify-between">
                <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400">
                  {item.detail}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
