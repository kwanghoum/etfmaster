import { Pool } from "pg";

// Vercel 서버리스 함수는 인스턴스가 재사용되므로 모듈 스코프 Pool을 공유한다.
// Neon 무료 플랜의 동시 접속 제한을 고려해 max를 작게 유지.
let pool: Pool | undefined;

export function getPool(): Pool {
  if (!pool) {
    const connectionString = process.env.DATABASE_URL;
    if (!connectionString) {
      throw new Error("DATABASE_URL 환경변수가 설정되지 않았습니다.");
    }
    pool = new Pool({
      connectionString,
      max: 3,
      idleTimeoutMillis: 30_000,
    });
  }
  return pool;
}

// FastAPI의 ETFResponse와 동일한 필드/직렬화 형태를 SQL 레벨에서 맞춘다:
// - BIGINT 컬럼은 pg 드라이버가 문자열로 반환하므로 float8로 캐스팅해 숫자로 받는다.
// - data_updated_at은 UTC ISO 문자열("+00:00" 접미사)로 포맷한다.
export const ETF_SELECT_FIELDS = `
  ticker, name, description, issuer, category, underlying_index, exchange,
  price,
  volume::float8 AS volume,
  market_cap::float8 AS market_cap,
  net_assets::float8 AS net_assets,
  inception_date::float8 AS inception_date,
  expense_ratio, dividend_yield,
  ex_dividend_date::float8 AS ex_dividend_date,
  return_1m, return_1y, return_3y, return_3y_avg, return_5y, return_5y_avg,
  to_char(data_updated_at, 'YYYY-MM-DD"T"HH24:MI:SS"+00:00"') AS data_updated_at
`;
