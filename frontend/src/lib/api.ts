import type { ETFListResponse, FilterOptions } from "@/types/etf";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export function fetchAllEtfs(): Promise<ETFListResponse> {
  return fetchJSON<ETFListResponse>("/api/etfs?per_page=0");
}

export function fetchFilters(): Promise<FilterOptions> {
  return fetchJSON<FilterOptions>("/api/etfs/filters");
}

export async function triggerSync(): Promise<void> {
  await fetch(`${API_BASE}/api/admin/sync`, { method: "POST" });
}
