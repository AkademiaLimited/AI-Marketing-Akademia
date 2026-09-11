from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from celery import chain

from app.core.database import get_db
from app.api.routers.auth import get_current_admin
from app.core.celery_app import celery_app
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductOut

router = APIRouter()


@router.get("/", response_model=list[ProductOut])
async def list_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    return result.scalars().all()


@router.get("/{slug}", response_model=ProductOut)
async def get_product(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.slug == slug))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductOut, status_code=201)
async def create_product(payload: ProductCreate, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    product = Product(**payload.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.patch("/{slug}", response_model=ProductOut)
async def update_product(slug: str, payload: dict, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Product).where(Product.slug == slug))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in payload.items():
        if hasattr(product, key):
            setattr(product, key, value)
    await db.commit()
    await db.refresh(product)
    return product


@router.post("/{slug}/publish", response_model=ProductOut)
async def publish_product(slug: str, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    """
    Publish a product and trigger the automated marketing pipeline.

    The product is marked as published instantly (green checkmark for the admin).
    A Celery chain is queued to: generate AI content → select channels →
    auto-publish to social media and email.
    """
    result = await db.execute(select(Product).where(Product.slug == slug))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.published = True
    product.marketing_status = "queued"
    await db.commit()
    await db.refresh(product)

    pipeline = chain(
        celery_app.signature("app.tasks.content.generate_content", args=[product.id]),
        celery_app.signature("app.tasks.content.select_channels"),
        celery_app.signature("app.tasks.content.publish_content"),
    )
    pipeline.apply_async()

    return product
