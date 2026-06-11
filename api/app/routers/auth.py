import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_db
from app.dependencies import hash_api_key
from app.models.api_key import APIKey
from app.schemas.auth import RegisterRequest, RegisterResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterResponse)
async def register(body: RegisterRequest, session: AsyncSession = Depends(get_db)):
    """Request a free API key. Store it safely — it is only shown once."""
    existing = await session.execute(select(APIKey).where(APIKey.email == body.email))
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="An API key for this email already exists.")

    raw_key = f"etmdb_{secrets.token_urlsafe(32)}"
    key_hash = hash_api_key(raw_key)
    prefix = raw_key[:8]

    api_key = APIKey(
        key_hash=key_hash,
        key_prefix=prefix,
        name=body.name,
        email=body.email,
        rate_limit=10_000,
    )
    session.add(api_key)
    await session.commit()

    return RegisterResponse(
        api_key=raw_key,
        name=body.name,
        email=body.email,
        rate_limit=10_000,
        message="Save your API key — it will not be shown again.",
    )
