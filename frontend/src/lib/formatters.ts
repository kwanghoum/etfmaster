export function formatPrice(value: number | null): string {
  if (value == null) return "--";
  return `$${value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function formatMarketCap(value: number | null): string {
  if (value == null) return "--";
  if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
  if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
  return `$${value.toLocaleString("en-US")}`;
}

export function formatPercent(value: number | null): string {
  if (value == null) return "--";
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
}

export function formatExpenseRatio(value: number | null): string {
  if (value == null) return "--";
  return `${value.toFixed(2)}%`;
}

export function returnColor(value: number | null): string {
  if (value == null) return "text-gray-400";
  if (value > 0) return "text-green-600";
  if (value < 0) return "text-red-600";
  return "text-gray-700";
}

export function formatVolume(value: number | null): string {
  if (value == null) return "--";
  if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
  if (value >= 1e3) return `${(value / 1e3).toFixed(0)}K`;
  return value.toLocaleString("en-US");
}

export function formatDateTime(value: string | null): string {
  if (value == null) return "--";
  const date = new Date(value);
  const formatted = date.toLocaleString("ko-KR", {
    timeZone: "Asia/Seoul",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });
  return `${formatted} (UTC+9)`;
}

export function formatTradingValue(price: number | null, volume: number | null): string {
  if (price == null || volume == null) return "--";
  const value = price * volume;
  if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
  if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
  return `$${value.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
}

export function formatInceptionDate(timestamp: number | null): string {
  if (timestamp == null) return "--";
  const date = new Date(timestamp);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatExDividendDate(timestamp: number | null): string {
  if (timestamp == null) return "--";
  const date = new Date(timestamp * 1000); // exDividendDate is in seconds
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}
