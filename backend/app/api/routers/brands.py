from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.brand import BrandProfile
from app.schemas.brand import BrandProfileCreate, BrandProfileOut, BrandProfileUpdate

router = APIRouter()


@router.get("/", response_model=list[BrandProfileOut])
async def list_brands(
    user_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List brand profiles, optionally filtered by user_id."""
    query = select(BrandProfile)
    if user_id:
        query = query.where(BrandProfile.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{brand_id}", response_model=BrandProfileOut)
async def get_brand(brand_id: str, db: AsyncSession = Depends(get_db)):
    brand = (await db.execute(select(BrandProfile).where(BrandProfile.id == brand_id))).scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    return brand


@router.get("/user/{user_id}", response_model=BrandProfileOut)
async def get_user_brand(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get the active brand profile for a user."""
    brand = (
        await db.execute(
            select(BrandProfile)
            .where(BrandProfile.user_id == user_id, BrandProfile.is_active.is_(True))
        )
    ).scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="No active brand profile for user")
    return brand


@router.post("/", response_model=BrandProfileOut, status_code=201)
async def create_brand(
    payload: BrandProfileCreate,
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    import uuid
    brand = BrandProfile(id=str(uuid.uuid4()), user_id=user_id, **payload.model_dump())
    db.add(brand)
    await db.commit()
    await db.refresh(brand)
    return brand


@router.patch("/{brand_id}", response_model=BrandProfileOut)
async def update_brand(
    brand_id: str,
    payload: BrandProfileUpdate,
    db: AsyncSession = Depends(get_db),
):
    brand = (await db.execute(select(BrandProfile).where(BrandProfile.id == brand_id))).scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(brand, field, value)
    await db.commit()
    await db.refresh(brand)
    return brand


@router.delete("/{brand_id}", status_code=204)
async def delete_brand(brand_id: str, db: AsyncSession = Depends(get_db)):
    brand = (await db.execute(select(BrandProfile).where(BrandProfile.id == brand_id))).scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    await db.delete(brand)
    await db.commit()
