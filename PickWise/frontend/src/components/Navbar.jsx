import React from 'react';
import { Scale, Moon, Sun, Sparkles, Smartphone, Laptop } from 'lucide-react';

export default function Navbar({ darkMode, setDarkMode, onSelectDemo, selectedCategory, setSelectedCategory }) {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white shadow-md shadow-emerald-500/20">
            <Scale className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-xl tracking-tight text-slate-900 dark:text-white">
                Pick<span className="text-emerald-500">Wise</span>
              </span>
              <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                Deterministic
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">
              Unbiased Multi-Criteria Decision Engine
            </p>
          </div>
        </div>

        {/* Category switcher & Actions */}
        <div className="flex items-center space-x-2 sm:space-x-4">
          
          {/* Category Toggle */}
          <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-lg text-xs font-medium">
            <button
              onClick={() => setSelectedCategory('smartphones')}
              className={`flex items-center space-x-1 px-3 py-1.5 rounded-md transition-all ${
                selectedCategory === 'smartphones'
                  ? 'bg-white dark:bg-slate-700 text-emerald-600 dark:text-emerald-400 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              <Smartphone className="w-3.5 h-3.5" />
              <span>Phones</span>
            </button>
            <button
              onClick={() => setSelectedCategory('laptops')}
              className={`flex items-center space-x-1 px-3 py-1.5 rounded-md transition-all ${
                selectedCategory === 'laptops'
                  ? 'bg-white dark:bg-slate-700 text-emerald-600 dark:text-emerald-400 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
              title="Category Extensibility Demo"
            >
              <Laptop className="w-3.5 h-3.5" />
              <span>Laptops</span>
            </button>
          </div>

          {/* Quick Sample Demo Button */}
          <button
            onClick={onSelectDemo}
            className="hidden md:flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-lg text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/50 hover:bg-emerald-100 dark:hover:bg-emerald-900 border border-emerald-200 dark:border-emerald-800 transition"
          >
            <Sparkles className="w-3.5 h-3.5 text-emerald-500" />
            <span>Load Sample Battle</span>
          </button>

          {/* Dark Mode Toggle */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-xl text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition"
            aria-label="Toggle Dark Mode"
          >
            {darkMode ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5 text-slate-600" />}
          </button>
        </div>

      </div>
    </header>
  );
}
