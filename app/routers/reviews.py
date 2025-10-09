from email.policy import default
from http.client import HTTPException
from typing import List

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from starlette.status import HTTP_403_FORBIDDEN

from app.auth import get_current_user, get_current_buyer
from app.db_depends import get_async_db
from app.schemas import Review as ReviewSchema, CreateReview
from app.models import (
    Review as ReviewModel,
    Product as ProductModel,
    User as UserModel,
)


router = APIRouter(prefix="/reviews", tags=["reviews"])


async def update_product_rating(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id, ReviewModel.is_active == True
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating
    await db.commit()


@router.get("/", response_model=List[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
    result = await db.scalars(select(ReviewModel).where(ReviewModel.is_active))
    all_reviews = result.all()
    return all_reviews


@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: CreateReview,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
):
    """Проверка на наличие товара по ID"""
    result = await db.scalars(
        select(ProductModel).where(ProductModel.id == review.product_id)
    )
    product = result.first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    """Проверка, что юзер является 'buyer'"""
    await get_current_buyer(current_user)
    """Проверка, что данный юзер еще не оставлял отзыв под этим товаром"""
    result = await db.scalars(
        select(ReviewModel).where(
            ReviewModel.product_id == review.product_id,
            ReviewModel.user_id == current_user.id,
        )
    )
    double_review = result.first()
    if double_review:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already made a review about this product!",
        )
    """Добавление нового отзыва в БД"""
    db_review = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    """Изменение рейтинга товара"""
    await update_product_rating(db, product.id)
    return db_review


@router.delete("/{review_id}", status_code=status.HTTP_200_OK)
async def delete_review(
    review_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Проверка есть активный отзыв с таким ID"""
    result = await db.scalars(
        select(ReviewModel).where(ReviewModel.id == review_id, ReviewModel.is_active)
    )
    db_review = result.first()
    if not db_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found."
        )
    """Проверка является ли активный юзер админом"""
    if not current_user.is_admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="You are not admin!")
    """Мягкое удаление отзыва"""
    db_review.is_active = False
    await db.commit()
    await db.refresh(db_review)
    return {"message": "Review deleted"}
