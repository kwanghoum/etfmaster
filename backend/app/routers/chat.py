import logging

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import OPENAI_API_KEY
from app.database import get_db
from app.models.etf import ETF
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger(__name__)


def _build_etf_context(db: Session) -> str:
    """AUM 기준 상위 100개 ETF 데이터를 텍스트로 반환."""
    etfs = (
        db.query(ETF)
        .filter(ETF.market_cap.isnot(None))
        .order_by(ETF.market_cap.desc())
        .limit(100)
        .all()
    )
    if not etfs:
        etfs = db.query(ETF).limit(100).all()

    lines = []
    for etf in etfs:
        parts = [f"[{etf.ticker}]"]
        if etf.name:
            parts.append(etf.name)
        if etf.category:
            parts.append(f"카테고리:{etf.category}")
        if etf.issuer:
            parts.append(f"운용사:{etf.issuer}")
        if etf.expense_ratio is not None:
            parts.append(f"보수:{etf.expense_ratio:.2f}%")
        if etf.dividend_yield is not None:
            parts.append(f"배당:{etf.dividend_yield:.2f}%")
        if etf.market_cap:
            parts.append(f"AUM:${etf.market_cap // 1_000_000:,}M")
        if etf.return_1y is not None:
            parts.append(f"1Y:{etf.return_1y:+.1f}%")
        if etf.return_3y_avg is not None:
            parts.append(f"3Y연평균:{etf.return_3y_avg:+.1f}%")
        lines.append(" | ".join(parts))

    return "\n".join(lines)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY 환경변수가 설정되지 않았습니다.",
        )

    etf_context = _build_etf_context(db)

    system_prompt = f"""당신은 ETF Master 서비스의 미국 ETF 전문 투자 어드바이저입니다.
아래는 현재 데이터베이스에서 자산 규모(AUM) 기준 상위 100개 ETF의 실시간 정보입니다.

{etf_context}

답변 지침:
- 사용자의 투자 목표, 리스크 허용도, 투자 기간을 파악하여 맞춤 추천하세요.
- ETF 추천 시 티커, 이름, 추천 이유(비용, 수익률, 카테고리 등)를 명확히 설명하세요.
- 투자에는 원금 손실 위험이 있음을 항상 안내하세요.
- 한국어로 간결하게 답변하세요.
- 데이터에 없는 ETF를 언급할 때는 "현재 DB에 해당 ETF 정보가 없을 수 있습니다"라고 안내하세요."""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in request.messages:
        messages.append({"role": msg.role, "content": msg.content})

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
        )
        return ChatResponse(message=response.choices[0].message.content)
    except Exception as e:
        logger.error("OpenAI API 오류: %s", e)
        raise HTTPException(status_code=500, detail=f"AI 응답 오류: {e}")
