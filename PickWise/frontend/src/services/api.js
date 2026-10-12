const API_BASE = '/api';

export async function fetchCategories() {
  const res = await fetch(`${API_BASE}/categories`);
  if (!res.ok) throw new Error('Failed to fetch categories');
  return res.json();
}

export async function fetchPresets(category = 'smartphones') {
  const res = await fetch(`${API_BASE}/presets?category=${category}`);
  if (!res.ok) throw new Error('Failed to fetch presets');
  return res.json();
}

export async function fetchChipsets() {
  const res = await fetch(`${API_BASE}/chipsets`);
  if (!res.ok) throw new Error('Failed to fetch chipsets');
  return res.json();
}

export async function extractProducts(urls, forceRefresh = false) {
  const res = await fetch(`${API_BASE}/extract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ urls, force_refresh: forceRefresh })
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error || 'Failed to extract product specifications');
  }
  return data;
}

export async function compareProducts({ products, urls, weights, category = 'smartphones' }) {
  const res = await fetch(`${API_BASE}/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ products, urls, weights, category })
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error || 'Comparison calculation failed');
  }
  return data;
}
