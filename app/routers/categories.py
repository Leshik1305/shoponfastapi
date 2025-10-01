from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.categories import Category as CategoryModel
from app.schemas import Category as CategorySchema, CategoryCreate
from app.db_depends import get_db


router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get("/", response_model=list[CategorySchema])
async def get_all_categories(db: Session = Depends(get_db)):
    stmt = select(CategoryModel).where(CategoryModel.is_active)
    categories = db.scalars(stmt).all()
    return categories


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    if category.parent_id is not None:
        stmt = select(CategoryModel).where(
            CategoryModel.id == category.parent_id, CategoryModel.is_active
        )
        parent = db.scalars(stmt).first()
        if not parent:
            raise HTTPException(status_code=400, detail="Parent category not found")

    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int, category: CategoryCreate, db: Session = Depends(get_db)
):
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id, CategoryModel.is_active
    )
    category_db = db.scalars(stmt).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    if category.parent_id is not None:
        parent_stmt = select(CategoryModel).where(
            CategoryModel.id == category_id, CategoryModel.is_active
        )
        parent = db.scalars(parent_stmt).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
    db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**category.model_dump())
    )
    db.commit()
    db.refresh(category_db)
    return category_db


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id, CategoryModel.is_active
    )
    category = db.scalars(stmt).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    category.is_active = False
    db.commit()
    return {"status": "success", "message": "Category marked as inactive"}
