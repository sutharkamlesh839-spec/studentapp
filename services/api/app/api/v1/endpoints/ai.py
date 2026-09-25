import httpx
from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser
from app.core.config import settings
from app.schemas.ai import AIAssistRequest, AIAssistResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/assist", response_model=AIAssistResponse)
async def assist(payload: AIAssistRequest, _current_user: CurrentUser) -> AIAssistResponse:
    """Call an optional OpenAI-compatible provider without storing student prompts."""
    if not settings.ai_provider_url or not settings.ai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI assistant is not configured. Add AI_PROVIDER_URL and AI_API_KEY on the server.",
        )
    messages = [
        {"role": "system", "content": "You are a careful CA study assistant. Explain concepts clearly, label uncertainty, and tell the student to verify official rules against primary sources."},
        {"role": "user", "content": f"{payload.context or ''}\n\n{payload.prompt}"},
    ]
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                f"{settings.ai_provider_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {settings.ai_api_key}"},
                json={"model": settings.ai_model, "messages": messages, "temperature": 0.2},
            )
            response.raise_for_status()
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="The configured AI provider could not answer right now") from exc
    return AIAssistResponse(
        answer=str(answer),
        model=settings.ai_model,
        disclaimer="AI output is educational assistance, not a substitute for official ICAI material or professional advice.",
    )
