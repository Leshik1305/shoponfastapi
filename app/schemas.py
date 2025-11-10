from datetime import datetime
from decimal import Decimal
from enum import IntEnum

from pydantic import BaseModel, Field, ConfigDict, EmailStr, PositiveInt
from typing import Optional, Annotated


class GradeEnum(IntEnum):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5


class CategoryCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Название категории (3-50 символов)",
    )
    parent_id: Optional[int] = Field(
        None, description="ID родительской категории, если есть"
    )


class Category(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор категории")
    name: str = Field(..., description="Название категории")
    parent_id: Optional[int] = Field(
        None, description="ID родительской категории, если есть"
    )
    is_active: bool = Field(..., description="Активна ли категория")

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Название товара (3-100 символов)",
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Описание товара (до 500 символов)"
    )
    price: float = Field(..., gt=0, description="Цена товара (больше 0)")
    image_url: Optional[str] = Field(
        None, max_length=200, description="URL изображения товара"
    )
    stock: int = Field(
        ..., ge=0, description="Количество товара на складе (0 или больше)"
    )
    category_id: int = Field(..., description="ID категории, к которой относится товар")


class Product(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор товара")
    name: str = Field(..., description="Название товара")
    description: Optional[str] = Field(None, description="Описание товара")
    price: float = Field(..., description="Цена товара")
    image_url: Optional[str] = Field(None, description="URL изображения товара")
    stock: int = Field(..., description="Количество товара на складе")
    category_id: int = Field(..., description="ID категории")
    is_active: bool = Field(..., description="Активность товара")
    rating: Decimal = Field(..., description="Рейтинг товара")

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr = Field(description="Email пользователя")
    password: str = Field(min_length=8, description="Пароль (минимум 8 символов)")
    role: str = Field(
        default="buyer",
        pattern="^(buyer|seller)$",
        description="Роль: 'buyer' или 'seller'",
    )


class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    role: str
    model_config = ConfigDict(from_attributes=True)


class CreateReview(BaseModel):
    product_id: Annotated[PositiveInt, Field(..., description="Идентификатор продукта")]
    comment: Annotated[Optional[str], Field(default=None, description="Текст отзыва")]
    grade: Annotated[GradeEnum, Field(default=GradeEnum.five, description="Оценка")]


class Review(BaseModel):
    id: Annotated[int, Field(..., description="Уникальный идентификатор отзыва")]
    user_id: Annotated[int, Field(..., description="Идентификатор автора")]
    product_id: Annotated[int, Field(..., description="Идентификатор продукта")]
    comment: Annotated[Optional[str], Field(None, description="Текст отзыва")]
    comment_date: Annotated[
        datetime,
        Field(default_factory=datetime.now, description="Дата и время создания"),
    ]
    grade: Annotated[int, Field(..., description="Оценка")]
    is_active: Annotated[bool, Field(True, description="Активность отзыва")]

    model_config = ConfigDict(from_attributes=True)


class ProductList(BaseModel):
    items: Annotated[list[Product], Field(description="Товары для текущей страницы")]
    total: Annotated[int, Field(ge=0, description="Общее количество товаров")]
    page: Annotated[int, Field(ge=1, description="Номер текущей страницы")]
    page_size: Annotated[int, Field(ge=1, description="Количество элементов на странице")]
    model_config = ConfigDict(from_attributes=True)