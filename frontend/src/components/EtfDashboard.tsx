"use client";

import { useCallback, useState } from "react";
import type { SortingState } from "@tanstack/react-table";
import { useEtfData } from "@/hooks/useEtfData";
import EtfTable from "./EtfTable";
import SearchBar from "./SearchBar";
import StatsBar from "./StatsBar";

export default function EtfDashboard() {
  const { data, isLoading, isError, error } = useEtfData();
  const [globalFilter, setGlobalFilter] = useState("");
  const [sorting, setSorting] = useState<SortingState>([]);
  const [filteredCount, setFilteredCount] = useState(0);

  const handleFilteredCount = useCallback((count: number) => {
    setFilteredCount(count);
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500 text-lg">Loading ETF data...</div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500 text-lg">
          Failed to load data: {(error as Error).message}
        </div>
      </div>
    );
  }

  const etfs = data?.items ?? [];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <SearchBar value={globalFilter} onChange={setGlobalFilter} />
        <StatsBar data={etfs} filtered={filteredCount || etfs.length} />
      </div>
      <EtfTable
        data={etfs}
        globalFilter={globalFilter}
        sorting={sorting}
        onSortingChange={setSorting}
        onFilteredCountChange={handleFilteredCount}
      />
    </div>
  );
}
