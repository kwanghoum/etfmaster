import type { ETFListResponse, FilterOptions } from "@/types/etf";

// 프로덕션(Vercel)에서는 same-origin의 Next.js API 라우트(/api/*)를 사용한다.
// 로컬 개발에서는 기본적으로 FastAPI 백엔드(localhost:8000)를 사용하고,
// NEXT_PUBLIC_API_URL="" 로 지정하면 로컬에서도 Next.js 라우트를 쓸 수 있다.
const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ??
  (process.env.NODE_ENV === "development" ? "http://localhost:8000" : "");

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
