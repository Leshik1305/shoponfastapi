from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


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

    model_config = ConfigDict(from_attributes=True)
