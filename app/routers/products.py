from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, update

from sqlalchemy.orm import Session

from app.db_depends import get_db
from app.models import Product as ProductModel, Category as CategoryModel
from app.schemas import Product as ProductSchema, ProductCreate


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema])
async def get_all_products(db: Session = Depends(get_db)):
    stmt = (
        select(ProductModel)
        .join(CategoryModel)
        .where(
            ProductModel.is_active,
            CategoryModel.is_active,
            # ProductModel.stock > 0,
        )
    )
    products = db.scalars(stmt).all()
    return products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    stmt = select(CategoryModel).where(
        CategoryModel.id == product.category_id, CategoryModel.is_active
    )
    category_db = db.scalars(stmt).first()
    if not category_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get(
    "/category/{category_id}",
    response_model=list[ProductSchema],
    status_code=status.HTTP_200_OK,
)
async def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id, CategoryModel.is_active
    )
    category = db.scalars(stmt).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    stmt = select(ProductModel).where(
        ProductModel.category_id == category_id, ProductModel.is_active
    )
    products = db.scalars(stmt).all()
    return products


@router.get(
    "/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK
)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    stmt = select(ProductModel).where(
        ProductModel.id == product_id, ProductModel.is_active
    )
    product = db.scalar(stmt)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    stmt = select(CategoryModel).where(
        CategoryModel.id == product.category_id, CategoryModel.is_active
    )
    category_db = db.scalar(stmt)
    if not category_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return product


@router.put(
    "/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK
)
async def update_product(
    product_id: int, product: ProductCreate, db: Session = Depends(get_db)
):
    stmt = select(ProductModel).where(
        ProductModel.id == product_id, ProductModel.is_active
    )
    product_to_update = db.scalars(stmt).first()
    if not product_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    stmt = select(CategoryModel).where(
        CategoryModel.id == product.category_id,
        CategoryModel.is_active,
    )
    category_db = db.scalars(stmt).first()
    if not category_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump())
    )
    db.commit()
    db.refresh(product_to_update)
    return product_to_update


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    stmt = select(ProductModel).where(
        ProductModel.id == product_id, ProductModel.is_active
    )
    product = db.scalars(stmt).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    stmt = select(CategoryModel).where(
        CategoryModel.id == product.category_id, CategoryModel.is_active
    )
    category_db = db.scalars(stmt).first()
    if not category_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    product.is_active = False
    db.commit()
    return {"status": "success", "message": "Product marked as inactive"}
