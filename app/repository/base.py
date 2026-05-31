"""Base repository with common CRUD operations."""

from typing import Generic, TypeVar, Optional, List, Type
from sqlalchemy.orm import Session
from sqlalchemy import select, func

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations."""

    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def create(self, obj_in: dict) -> T:
        """Create a new record."""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_id(self, id: int) -> Optional[T]:
        """Get record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def update(self, id: int, obj_in: dict) -> Optional[T]:
        """Update a record."""
        db_obj = self.get_by_id(id)
        if db_obj:
            for key, value in obj_in.items():
                if value is not None:
                    setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> bool:
        """Soft delete a record (mark as deleted)."""
        db_obj = self.get_by_id(id)
        if db_obj and hasattr(db_obj, 'is_deleted'):
            db_obj.is_deleted = True
            self.db.commit()
            return True
        return False

    def hard_delete(self, id: int) -> bool:
        """Hard delete a record from database."""
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False

    def count(self) -> int:
        """Get total count of records."""
        return self.db.query(func.count(self.model.id)).scalar()

    def count_active(self) -> int:
        """Get count of active (non-deleted) records."""
        if hasattr(self.model, 'is_deleted'):
            return self.db.query(func.count(self.model.id)).filter(
                self.model.is_deleted == False
            ).scalar()
        return self.count()
