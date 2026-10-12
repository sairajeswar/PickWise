import React, { useState } from 'react';
import { Plus, Trash2, Sliders, Play, AlertCircle, Sparkles, CheckCircle2 } from 'lucide-react';

const PRESET_ICONS = {
  Balanced: '⚖️',
  Gaming: '🎮',
  Camera: '📸',
  Battery: '🔋',
  Budget: '💰'
};

export default function UrlInputForm({
  urls,
  setUrls,
  presets,
  selectedPreset,
  setSelectedPreset,
  weights,
  setWeights,
  groupLabels,
  onSubmit,
  isLoading,
  error,
  setError
}) {
  const [showSliders, setShowSliders] = useState(false);

  const addUrlField = () => {
    if (urls.length >= 5) {
      setError("Maximum 5 product links allowed.");
      return;
    }
    setError(null);
    setUrls([...urls, '']);
  };

  const removeUrlField = (index) => {
    if (urls.length <= 2) {
      setError("At least 2 product links are required for comparison.");
      return;
    }
    setError(null);
    const newUrls = urls.filter((_, i) => i !== index);
    setUrls(newUrls);
  };

  const handleUrlChange = (index, value) => {
    setError(null);
    const newUrls = [...urls];
    newUrls[index] = value;
    setUrls(newUrls);
  };

  const handlePresetSelect = (presetName) => {
    setSelectedPreset(presetName);
    if (presets && presets[presetName]) {
      setWeights({ ...presets[presetName] });
    }
  };

  const handleSliderChange = (groupKey, value) => {
    setSelectedPreset('Custom');
    setWeights(prev => ({
      ...prev,
      [groupKey]: parseFloat(value)
    }));
  };

  const totalWeight = Object.values(weights || {}).reduce((a, b) => a + (parseFloat(b) || 0), 0);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 sm:p-8 shadow-sm border border-slate-200 dark:border-slate-800 transition">
      
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
          Compare Products
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Paste 2 to 5 links from Flipkart or Amazon. Pick a preset or adjust weight sliders to prioritize what matters to you.
        </p>
      </div>

      {/* URL Inputs */}
      <div className="space-y-3 mb-6">
        {urls.map((url, idx) => (
          <div key={idx} className="flex items-center space-x-2">
            <span className="flex-shrink-0 w-7 h-7 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 flex items-center justify-center text-xs font-semibold">
              {idx + 1}
            </span>
            <div className="relative flex-1">
              <input
                type="url"
                value={url}
                onChange={(e) => handleUrlChange(idx, e.target.value)}
                placeholder={`Paste Flipkart or Amazon link #${idx + 1}...`}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/60 text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500 transition"
              />
            </div>
            {urls.length > 2 && (
              <button
                type="button"
                onClick={() => removeUrlField(idx)}
                className="p-2.5 text-slate-400 hover:text-rose-500 rounded-xl hover:bg-rose-50 dark:hover:bg-rose-950/30 transition"
                title="Remove link"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        ))}

        {urls.length < 5 && (
          <button
            type="button"
            onClick={addUrlField}
            className="flex items-center space-x-1.5 text-xs font-medium text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 py-1.5 px-3 rounded-lg hover:bg-emerald-50 dark:hover:bg-emerald-950/40 transition"
          >
            <Plus className="w-4 h-4" />
            <span>Add Another Product Link ({urls.length}/5)</span>
          </button>
        )}
      </div>

      {/* Error Alert */}
      {error && (
        <div className="mb-6 p-4 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800/50 flex items-start space-x-3 text-rose-700 dark:text-rose-400 text-sm animate-shake">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5 text-rose-500" />
          <div className="flex-1 font-medium">{error}</div>
        </div>
      )}

      {/* Priority Presets */}
      <div className="mb-6">
        <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2.5">
          Priority Preset
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
          {Object.keys(presets || {}).map((pName) => {
            const isSelected = selectedPreset === pName;
            return (
              <button
                key={pName}
                type="button"
                onClick={() => handlePresetSelect(pName)}
                className={`flex items-center justify-center space-x-2 px-3 py-2.5 rounded-xl border text-xs font-medium transition ${
                  isSelected
                    ? 'border-emerald-500 bg-emerald-50/80 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 ring-2 ring-emerald-500/20'
                    : 'border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-700 bg-white dark:bg-slate-800'
                }`}
              >
                <span>{PRESET_ICONS[pName] || '🎯'}</span>
                <span>{pName}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Weight Sliders Drawer Toggle */}
      <div className="mb-6">
        <button
          type="button"
          onClick={() => setShowSliders(!showSliders)}
          className="flex items-center space-x-2 text-xs font-medium text-slate-600 dark:text-slate-300 hover:text-emerald-600 dark:hover:text-emerald-400 transition"
        >
          <Sliders className="w-4 h-4 text-emerald-500" />
          <span>{showSliders ? 'Hide Category Weight Sliders' : 'Fine-Tune Category Weights with Sliders'}</span>
          {selectedPreset === 'Custom' && (
            <span className="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
              Custom
            </span>
          )}
        </button>

        {showSliders && (
          <div className="mt-4 p-5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 space-y-4">
            <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 pb-2 border-b border-slate-200 dark:border-slate-700">
              <span>Category</span>
              <span>Weight ({totalWeight}%)</span>
            </div>
            {Object.keys(weights || {}).map((groupKey) => {
              const label = groupLabels?.[groupKey] || groupKey.toUpperCase();
              const val = weights[groupKey] || 0;
              return (
                <div key={groupKey} className="space-y-1">
                  <div className="flex justify-between text-xs font-medium text-slate-700 dark:text-slate-300">
                    <span>{label}</span>
                    <span className="text-emerald-600 dark:text-emerald-400 font-semibold">{val}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="60"
                    step="5"
                    value={val}
                    onChange={(e) => handleSliderChange(groupKey, e.target.value)}
                    className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                  />
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Start Filter Action */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
        <div className="flex items-center space-x-2 text-xs text-slate-400">
          <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          <span>Min 2 &bull; Max 5 products &bull; 30-min cached specs</span>
        </div>
        <button
          type="button"
          disabled={isLoading}
          onClick={onSubmit}
          className="w-full sm:w-auto flex items-center justify-center space-x-2 px-8 py-3.5 rounded-xl font-semibold text-sm text-white bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 shadow-lg shadow-emerald-600/25 hover:shadow-emerald-600/35 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Analyzing Specs...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-white" />
              <span>Start Filter</span>
            </>
          )}
        </button>
      </div>

    </div>
  );
}
