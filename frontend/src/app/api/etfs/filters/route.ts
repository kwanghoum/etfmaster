import { NextResponse } from "next/server";

import { getPool } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const pool = getPool();
    const [cats, iss] = await Promise.all([
      pool.query(
        "SELECT DISTINCT category FROM etfs WHERE category IS NOT NULL ORDER BY category",
      ),
      pool.query("SELECT DISTINCT issuer FROM etfs WHERE issuer IS NOT NULL ORDER BY issuer"),
    ]);
    return NextResponse.json({
      categories: cats.rows.map((r) => r.category),
      issuers: iss.rows.map((r) => r.issuer),
    });
  } catch (e) {
    console.error("GET /api/etfs/filters failed:", e);
    return NextResponse.json({ detail: "Database query failed" }, { status: 500 });
  }
}
