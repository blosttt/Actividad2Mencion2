from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
import models
import schemas

class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[models.Categorias]:
        return self.db.query(models.Categorias).all()

    def get_by_id(self, categoria_id: int) -> Optional[models.Categorias]:
        return self.db.query(models.Categorias).filter(
            models.Categorias.id_categoria == categoria_id
        ).first()

    def get_by_nombre(self, nombre_categoria: str) -> Optional[models.Categorias]:
        return self.db.query(models.Categorias).filter(
            models.Categorias.nombre_categoria == nombre_categoria
        ).first()

    def create(self, categoria: schemas.CategoriaCreate) -> models.Categorias:
        db_categoria = models.Categorias(**categoria.model_dump())
        self.db.add(db_categoria)
        self.db.commit()
        self.db.refresh(db_categoria)
        return db_categoria

    def update(self, categoria_id: int, categoria_update: schemas.CategoriaCreate) -> Optional[models.Categorias]:
        db_categoria = self.get_by_id(categoria_id)
        if not db_categoria:
            return None
        update_data = categoria_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_categoria, field, value)
        self.db.commit()
        self.db.refresh(db_categoria)
        return db_categoria

    def delete(self, categoria_id: int) -> bool:
        db_categoria = self.get_by_id(categoria_id)
        if not db_categoria:
            return False
        self.db.delete(db_categoria)
        self.db.commit()
        return True