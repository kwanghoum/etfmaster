"use client";

import type { ETF } from "@/types/etf";
import { formatMarketCap } from "@/lib/formatters";

interface StatsBarProps {
  data: ETF[];
  filtered: number;
}

export default function StatsBar({ data, filtered }: StatsBarProps) {
  const totalAum = data.reduce((sum, e) => sum + (e.market_cap ?? 0), 0);
  const avgExpense = (() => {
    const valid = data.filter((e) => e.expense_ratio != null);
    if (valid.length === 0) return null;
    return valid.reduce((s, e) => s + e.expense_ratio!, 0) / valid.length;
  })();

  return (
    <div className="flex flex-wrap gap-6 text-sm text-gray-600">
      <div>
        <span className="font-medium text-gray-900">{data.length.toLocaleString()}</span> Total ETFs
      </div>
      {filtered !== data.length && (
        <div>
          <span className="font-medium text-gray-900">{filtered.toLocaleString()}</span> Shown
        </div>
      )}
      <div>
        Total AUM: <span className="font-medium text-gray-900">{formatMarketCap(totalAum)}</span>
      </div>
      {avgExpense != null && (
        <div>
          Avg Expense: <span className="font-medium text-gray-900">{avgExpense.toFixed(2)}%</span>
        </div>
      )}
    </div>
  );
}
