import React, { useState } from 'react';
import { X, AlertTriangle, Cpu, Save, ShieldAlert } from 'lucide-react';

export default function FallbackModal({
  product,
  chipsets,
  onSave,
  onClose
}) {
  const [formData, setFormData] = useState({
    name: product?.name || '',
    price: product?.specs?.price || '',
    mrp: product?.specs?.mrp || '',
    chipset: product?.specs?.chipset || '',
    ram: product?.specs?.ram || '',
    storage: product?.specs?.storage || '',
    battery_capacity: product?.specs?.battery_capacity || '',
    charging_speed: product?.specs?.charging_speed || '',
    rear_camera: product?.specs?.rear_camera || '',
    front_camera: product?.specs?.front_camera || '',
    display_size: product?.specs?.display_size || '',
    refresh_rate: product?.specs?.refresh_rate || '120',
    display_type: product?.specs?.display_type || 'AMOLED',
    rating: product?.specs?.rating || '4.3',
    review_count: product?.specs?.review_count || '1500'
  });

  const handleChange = (field, val) => {
    setFormData(prev => ({ ...prev, [field]: val }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const updatedProduct = {
      ...product,
      name: formData.name || 'Custom Product',
      status: 'success',
      error: null,
      specs: {
        ...product.specs,
        price: parseFloat(formData.price) || 0,
        mrp: parseFloat(formData.mrp) || parseFloat(formData.price) || 0,
        chipset: formData.chipset,
        ram: parseFloat(formData.ram) || 8,
        storage: parseFloat(formData.storage) || 128,
        battery_capacity: parseFloat(formData.battery_capacity) || 5000,
        charging_speed: parseFloat(formData.charging_speed) || 33,
        rear_camera: parseFloat(formData.rear_camera) || 50,
        front_camera: parseFloat(formData.front_camera) || 16,
        display_size: parseFloat(formData.display_size) || 6.7,
        refresh_rate: parseFloat(formData.refresh_rate) || 120,
        display_type: formData.display_type,
        rating: parseFloat(formData.rating) || 4.2,
        review_count: parseInt(formData.review_count) || 1000
      }
    };
    onSave(updatedProduct);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm overflow-y-auto">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl max-w-2xl w-full max-h-[90vh] flex flex-col shadow-2xl transition">
        
        {/* Header */}
        <div className="p-6 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-amber-100 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                Manual Spec Fallback
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {product?.url ? product.url.substring(0, 50) + '...' : 'Product specifications'}
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

        {/* Notice */}
        <div className="px-6 pt-4">
          <div className="p-3.5 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/40 text-xs text-amber-800 dark:text-amber-300 flex items-start space-x-2.5">
            <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>
              {product?.error || "Automated scraper was blocked or could not read all specs. Enter or adjust the specs manually to proceed with the decision score."}
            </span>
          </div>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto space-y-4 flex-1">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Product Title / Model Name
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="e.g. OnePlus Nord CE4 5G"
              className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Selling Price (₹)
              </label>
              <input
                type="number"
                required
                value={formData.price}
                onChange={(e) => handleChange('price', e.target.value)}
                placeholder="24999"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-emerald-500/20"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                MRP (₹)
              </label>
              <input
                type="number"
                value={formData.mrp}
                onChange={(e) => handleChange('mrp', e.target.value)}
                placeholder="27999"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
          </div>

          {/* Chipset / Processor */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Processor / Chipset
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                list="chipset-list"
                value={formData.chipset}
                onChange={(e) => handleChange('chipset', e.target.value)}
                placeholder="e.g. Snapdragon 7 Gen 3"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
              <datalist id="chipset-list">
                {chipsets?.map(c => (
                  <option key={c.name} value={c.name}>
                    {c.name} ({c.score}/100)
                  </option>
                ))}
              </datalist>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                RAM (GB)
              </label>
              <input
                type="number"
                value={formData.ram}
                onChange={(e) => handleChange('ram', e.target.value)}
                placeholder="8"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Storage (GB)
              </label>
              <input
                type="number"
                value={formData.storage}
                onChange={(e) => handleChange('storage', e.target.value)}
                placeholder="128"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Battery (mAh)
              </label>
              <input
                type="number"
                value={formData.battery_capacity}
                onChange={(e) => handleChange('battery_capacity', e.target.value)}
                placeholder="5000"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Charging Speed (W)
              </label>
              <input
                type="number"
                value={formData.charging_speed}
                onChange={(e) => handleChange('charging_speed', e.target.value)}
                placeholder="67"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Rear Camera (MP)
              </label>
              <input
                type="number"
                value={formData.rear_camera}
                onChange={(e) => handleChange('rear_camera', e.target.value)}
                placeholder="50"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Front Camera (MP)
              </label>
              <input
                type="number"
                value={formData.front_camera}
                onChange={(e) => handleChange('front_camera', e.target.value)}
                placeholder="16"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Screen (Inches)
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.display_size}
                onChange={(e) => handleChange('display_size', e.target.value)}
                placeholder="6.7"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Refresh (Hz)
              </label>
              <input
                type="number"
                value={formData.refresh_rate}
                onChange={(e) => handleChange('refresh_rate', e.target.value)}
                placeholder="120"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Display Tech
              </label>
              <select
                value={formData.display_type}
                onChange={(e) => handleChange('display_type', e.target.value)}
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              >
                <option value="AMOLED">AMOLED / OLED</option>
                <option value="IPS LCD">IPS LCD</option>
                <option value="LCD">LCD</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Rating (1 - 5)
              </label>
              <input
                type="number"
                step="0.1"
                max="5"
                min="1"
                value={formData.rating}
                onChange={(e) => handleChange('rating', e.target.value)}
                placeholder="4.3"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Reviews Count
              </label>
              <input
                type="number"
                value={formData.review_count}
                onChange={(e) => handleChange('review_count', e.target.value)}
                placeholder="2500"
                className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
          </div>

          <div className="pt-4 flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex items-center space-x-2 px-6 py-2.5 rounded-xl text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-500 shadow-md shadow-emerald-600/20"
            >
              <Save className="w-4 h-4" />
              <span>Save & Use Specs</span>
            </button>
          </div>
        </form>

      </div>
    </div>
  );
}
