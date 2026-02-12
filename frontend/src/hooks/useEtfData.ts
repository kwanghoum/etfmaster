"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchAllEtfs, fetchFilters } from "@/lib/api";

export function useEtfData() {
  return useQuery({
    queryKey: ["etfs"],
    queryFn: fetchAllEtfs,
    staleTime: 5 * 60 * 1000,
    refetchInterval: 5 * 60 * 1000,
  });
}

export function useEtfFilters() {
  return useQuery({
    queryKey: ["etf-filters"],
    queryFn: fetchFilters,
    staleTime: 30 * 60 * 1000,
  });
}
