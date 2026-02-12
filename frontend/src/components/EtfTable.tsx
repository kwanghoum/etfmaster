"use client";

import { useEffect, useRef } from "react";
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
  type SortingState,
} from "@tanstack/react-table";
import { useVirtualizer } from "@tanstack/react-virtual";
import type { ETF } from "@/types/etf";
import { columns } from "./EtfTableColumns";

interface EtfTableProps {
  data: ETF[];
  globalFilter: string;
  sorting: SortingState;
  onSortingChange: (s: SortingState) => void;
  onFilteredCountChange: (count: number) => void;
}

export default function EtfTable({
  data,
  globalFilter,
  sorting,
  onSortingChange,
  onFilteredCountChange,
}: EtfTableProps) {
  const parentRef = useRef<HTMLDivElement>(null);

  const table = useReactTable({
    data,
    columns,
    state: { sorting, globalFilter },
    onSortingChange: (updater) => {
      const next = typeof updater === "function" ? updater(sorting) : updater;
      onSortingChange(next);
    },
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    globalFilterFn: "includesString",
  });

  const { rows } = table.getRowModel();

  useEffect(() => {
    onFilteredCountChange(rows.length);
  }, [rows.length, onFilteredCountChange]);

  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 40,
    overscan: 10,
  });

  return (
    <div
      ref={parentRef}
      className="overflow-auto border border-gray-200 rounded-lg"
      style={{ height: "calc(100vh - 200px)" }}
    >
      <table className="w-full text-sm">
        <thead className="sticky top-0 z-10 bg-gray-50 border-b border-gray-200">
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id}>
              {hg.headers.map((header) => (
                <th
                  key={header.id}
                  className="px-3 py-2 text-left font-medium text-gray-700 whitespace-nowrap cursor-pointer select-none hover:bg-gray-100"
                  style={{ width: header.getSize() }}
                  onClick={header.column.getToggleSortingHandler()}
                >
                  <div className="flex items-center gap-1">
                    {flexRender(header.column.columnDef.header, header.getContext())}
                    {{ asc: " \u25B2", desc: " \u25BC" }[
                      header.column.getIsSorted() as string
                    ] ?? ""}
                  </div>
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          <tr style={{ height: `${virtualizer.getVirtualItems()[0]?.start ?? 0}px` }}>
            <td colSpan={columns.length} />
          </tr>
          {virtualizer.getVirtualItems().map((vRow) => {
            const row = rows[vRow.index];
            return (
              <tr
                key={row.id}
                className="border-b border-gray-100 hover:bg-blue-50 transition-colors"
                style={{ height: `${vRow.size}px` }}
              >
                {row.getVisibleCells().map((cell) => (
                  <td
                    key={cell.id}
                    className="px-3 py-1.5 whitespace-nowrap"
                    style={{ width: cell.column.getSize() }}
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            );
          })}
          <tr
            style={{
              height: `${virtualizer.getTotalSize() - (virtualizer.getVirtualItems().at(-1)?.end ?? 0)}px`,
            }}
          >
            <td colSpan={columns.length} />
          </tr>
        </tbody>
      </table>
    </div>
  );
}
