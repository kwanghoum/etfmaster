import { NextRequest, NextResponse } from "next/server";

import { ETF_SELECT_FIELDS, getPool } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ ticker: string }> },
) {
  const { ticker } = await params;

  try {
    const pool = getPool();
    const res = await pool.query(
      `SELECT ${ETF_SELECT_FIELDS} FROM etfs WHERE upper(ticker) = upper($1) LIMIT 1`,
      [ticker],
    );
    return NextResponse.json(res.rows[0] ?? null);
  } catch (e) {
    console.error("GET /api/etfs/[ticker] failed:", e);
    return NextResponse.json({ detail: "Database query failed" }, { status: 500 });
  }
}
