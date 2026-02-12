import { createColumnHelper } from "@tanstack/react-table";
import type { ETF } from "@/types/etf";
import {
  formatDateTime,
  formatExpenseRatio,
  formatInceptionDate,
  formatMarketCap,
  formatPercent,
  formatPrice,
  formatTradingValue,
  formatVolume,
  returnColor,
} from "@/lib/formatters";
import Tooltip from "./Tooltip";
import { ExternalLink, Globe } from "lucide-react";

const col = createColumnHelper<ETF>();

// Exchange code to full name mapping
const exchangeNames: Record<string, string> = {
  NYQ: "NYSE (New York Stock Exchange)",
  NGM: "Nasdaq Global Market",
  NMS: "Nasdaq Global Select Market",
  NCM: "Nasdaq Capital Market",
  PCX: "NYSE Arca",
  BTS: "CBOE (Chicago Board Options Exchange)",
  BZX: "CBOE BZX Exchange",
  NAS: "Nasdaq",
  ASE: "NYSE American",
  PSE: "NYSE Arca (formerly Pacific Stock Exchange)",
};

export const columns = [
  col.accessor("ticker", {
    header: "Ticker",
    size: 80,
    enableSorting: true,
    cell: (info) => {
      const ticker = info.getValue();
      return (
        <div className="group relative flex items-center gap-1.5">
          <span className="font-semibold text-blue-700">
            {ticker}
          </span>
          <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
            <a
              href={`https://finance.yahoo.com/quote/${ticker}/`}
              target="_blank"
              rel="noopener noreferrer"
              className="p-0.5 hover:bg-blue-100 rounded text-blue-600 hover:text-blue-800"
              title="Yahoo Finance"
            >
              <ExternalLink size={14} />
            </a>
            <a
              href={`https://www.etf.com/${ticker}`}
              target="_blank"
              rel="noopener noreferrer"
              className="p-0.5 hover:bg-green-100 rounded text-green-600 hover:text-green-800"
              title="ETF.com"
            >
              <Globe size={14} />
            </a>
          </div>
        </div>
      );
    },
  }),
  col.accessor("name", {
    header: "Name",
    size: 240,
    enableSorting: true,
    cell: (info) => {
      const name = info.getValue();
      const description = info.row.original.description;
      return (
        <Tooltip content={description}>
          {name ?? "--"}
        </Tooltip>
      );
    },
  }),
  col.accessor("exchange", {
    header: "Exchange",
    size: 90,
    enableSorting: true,
    cell: (info) => {
      const exchange = info.getValue();
      if (!exchange) return "--";
      const fullName = exchangeNames[exchange];
      return fullName ? (
        <Tooltip content={fullName}>
          {exchange}
        </Tooltip>
      ) : (
        exchange
      );
    },
  }),
  col.accessor("issuer", {
    header: "Issuer",
    size: 160,
    enableSorting: true,
    cell: (info) => info.getValue() ?? "--",
  }),
  col.accessor("category", {
    header: "Category",
    size: 180,
    enableSorting: true,
    cell: (info) => info.getValue() ?? "--",
  }),
  col.accessor("price", {
    header: "Price",
    size: 100,
    enableSorting: true,
    cell: (info) => formatPrice(info.getValue()),
  }),
  col.accessor("volume", {
    header: "Volume",
    size: 100,
    enableSorting: true,
    cell: (info) => formatVolume(info.getValue()),
  }),
  col.accessor(
    (row) => (row.price ?? 0) * (row.volume ?? 0),
    {
      id: "trading_value",
      header: "Trading Value",
      size: 120,
      enableSorting: true,
      cell: (info) => {
        const price = info.row.original.price;
        const volume = info.row.original.volume;
        return formatTradingValue(price, volume);
      },
    }
  ),
  col.accessor("net_assets", {
    header: "Net Assets",
    size: 120,
    enableSorting: true,
    cell: (info) => formatMarketCap(info.getValue()),
  }),
  col.accessor("expense_ratio", {
    header: "Expense Ratio",
    size: 120,
    enableSorting: true,
    cell: (info) => formatExpenseRatio(info.getValue()),
  }),
  col.accessor("dividend_yield", {
    header: "Div Yield",
    size: 100,
    enableSorting: true,
    cell: (info) => formatExpenseRatio(info.getValue()),
  }),
  col.accessor("return_1m", {
    header: "1M Return",
    size: 100,
    enableSorting: true,
    cell: (info) => {
      const v = info.getValue();
      return <span className={returnColor(v)}>{formatPercent(v)}</span>;
    },
  }),
  col.accessor("return_1y", {
    header: "1Y Return",
    size: 100,
    enableSorting: true,
    cell: (info) => {
      const v = info.getValue();
      return <span className={returnColor(v)}>{formatPercent(v)}</span>;
    },
  }),
  col.accessor("return_3y", {
    header: "3Y Return",
    size: 100,
    enableSorting: true,
    cell: (info) => {
      const v = info.getValue();
      return <span className={returnColor(v)}>{formatPercent(v)}</span>;
    },
  }),
  col.accessor("return_3y_avg", {
    header: "3Y Avg",
    size: 100,
    enableSorting: true,
    cell: (info) => {
      const v = info.getValue();
      return <span className={returnColor(v)}>{formatPercent(v)}</span>;
    },
  }),
  col.accessor("return_5y", {
    header: "5Y Return",
    size: 100,
    enableSorting: true,
    cell: (info) => {
      const v = info.getValue();
      return <span className={returnColor(v)}>{formatPercent(v)}</span>;
    },
  }),
  col.accessor("return_5y_avg", {
    header: "5Y Avg",
    size: 100,
    enableSorting: true,
    cell: (info) => {
      const v = info.getValue();
      return <span className={returnColor(v)}>{formatPercent(v)}</span>;
    },
  }),
  col.accessor("inception_date", {
    header: "Inception Date",
    size: 130,
    enableSorting: true,
    cell: (info) => formatInceptionDate(info.getValue()),
  }),
  col.accessor("data_updated_at", {
    header: "Last Updated",
    size: 180,
    enableSorting: true,
    cell: (info) => (
      <span className="text-xs text-gray-500">{formatDateTime(info.getValue())}</span>
    ),
  }),
];
