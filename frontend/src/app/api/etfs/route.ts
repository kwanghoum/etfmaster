import { NextRequest, NextResponse } from "next/server";

import { ETF_SELECT_FIELDS, getPool } from "@/lib/db";

export const dynamic = "force-dynamic";

const SORT_COLUMNS = new Set([
  "ticker",
  "name",
  "issuer",
  "category",
  "exchange",
  "price",
  "volume",
  "market_cap",
  "net_assets",
  "inception_date",
  "expense_ratio",
  "dividend_yield",
  "ex_dividend_date",
  "return_1m",
  "return_1y",
  "return_3y_avg",
  "return_5y",
  "return_5y_avg",
  "data_updated_at",
]);

export async function GET(req: NextRequest) {
  const sp = req.nextUrl.searchParams;

  const sortByParam = sp.get("sort_by") ?? "ticker";
  const sortBy = SORT_COLUMNS.has(sortByParam) ? sortByParam : "ticker";
  const sortDir = sp.get("sort_dir") === "desc" ? "DESC" : "ASC";
  const search = sp.get("search");
  const category = sp.get("category");
  const issuer = sp.get("issuer");
  const page = Math.max(1, parseInt(sp.get("page") ?? "1", 10) || 1);
  const perPage = Math.min(5000, Math.max(0, parseInt(sp.get("per_page") ?? "0", 10) || 0));

  const where: string[] = [];
  const params: unknown[] = [];

  if (search) {
    params.push(`%${search}%`);
    where.push(`(ticker ILIKE $${params.length} OR name ILIKE $${params.length})`);
  }
  if (category) {
    params.push(category);
    where.push(`category = $${params.length}`);
  }
  if (issuer) {
    params.push(issuer);
    where.push(`issuer = $${params.length}`);
  }

  const whereSql = where.length ? `WHERE ${where.join(" AND ")}` : "";

  let pagingSql = "";
  const listParams = [...params];
  if (perPage > 0) {
    listParams.push(perPage);
    pagingSql = ` LIMIT $${listParams.length}`;
    listParams.push((page - 1) * perPage);
    pagingSql += ` OFFSET $${listParams.length}`;
  }

  try {
    const pool = getPool();
    const [countRes, listRes] = await Promise.all([
      pool.query(`SELECT count(*)::int AS total FROM etfs ${whereSql}`, params),
      pool.query(
        `SELECT ${ETF_SELECT_FIELDS} FROM etfs ${whereSql} ORDER BY ${sortBy} ${sortDir}${pagingSql}`,
        listParams,
      ),
    ]);
    return NextResponse.json({ items: listRes.rows, total: countRes.rows[0].total });
  } catch (e) {
    console.error("GET /api/etfs failed:", e);
    return NextResponse.json({ detail: "Database query failed" }, { status: 500 });
  }
}
