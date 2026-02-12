export interface ETF {
  ticker: string;
  name: string | null;
  description: string | null;
  issuer: string | null;
  category: string | null;
  underlying_index: string | null;
  exchange: string | null;
  price: number | null;
  volume: number | null;
  market_cap: number | null;
  net_assets: number | null;
  inception_date: number | null;
  expense_ratio: number | null;
  dividend_yield: number | null;
  ex_dividend_date: number | null;
  return_1m: number | null;
  return_1y: number | null;
  return_3y: number | null;
  return_3y_avg: number | null;
  return_5y: number | null;
  return_5y_avg: number | null;
  data_updated_at: string | null;
}

export interface ETFListResponse {
  items: ETF[];
  total: number;
}

export interface FilterOptions {
  categories: string[];
  issuers: string[];
}
