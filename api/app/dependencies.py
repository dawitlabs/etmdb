import hashlib
from datetime import UTC, datetime

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.config import settings
from app.database import get_db
from app.exceptions import RateLimitError
from app.models.api_key import APIKey


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256((settings.api_key_salt + raw_key).encode()).hexdigest()


async def verify_api_key(
    x_api_key: str | None = Header(default=None, alias="X-Api-Key"),
    session: AsyncSession = Depends(get_db),
) -> APIKey:
    if not x_api_key:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Missing API key. Pass X-Api-Key header.")

    key_hash = hash_api_key(x_api_key)
    result = await session.execute(select(APIKey).where(APIKey.key_hash == key_hash))
    api_key = result.scalars().first()

    if not api_key or not api_key.is_active:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Invalid API key")

    today = datetime.now(UTC).date()
    if api_key.last_reset < today:
        api_key.requests_today = 0
        api_key.last_reset = today

    if api_key.requests_today >= api_key.rate_limit:
        raise RateLimitError()

    api_key.requests_today += 1
    session.add(api_key)
    await session.commit()
    return api_key
