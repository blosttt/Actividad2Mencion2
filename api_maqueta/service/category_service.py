from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
import models
import schemas

class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[models.Categoria]:
        return self.db.query(models.Categoria).filter(
            models.Categoria.activo == 1
        ).all()

    def get_by_id(self, categoria_id: int) -> Optional[models.Categoria]:
        return self.db.query(models.Categoria).filter(
            and_(
                models.Categoria.id == categoria_id,
                models.Categoria.activo == 1
            )
        ).first()

    def get_by_tipo(self, tipo: str) -> List[models.Categoria]:
        return self.db.query(models.Categoria).filter(
            and_(
                models.Categoria.tipo == tipo,
                models.Categoria.activo == 1
            )
        ).all()

    def create(self, categoria: schemas.CategoriaCreate) -> models.Categoria:
        db_categoria = models.Categoria(**categoria.model_dump())
        self.db.add(db_categoria)
        self.db.commit()
        self.db.refresh(db_categoria)
        return db_categoria