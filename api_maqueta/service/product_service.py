from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict
import models
import schemas

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[models.Productos]:
        return self.db.query(models.Productos).offset(skip).limit(limit).all()

    def get_by_id(self, producto_id: int) -> Optional[models.Productos]:
        return self.db.query(models.Productos).filter(
            models.Productos.id_producto == producto_id
        ).first()

    def get_by_codigo_producto(self, codigo_producto: str) -> Optional[models.Productos]:
        return self.db.query(models.Productos).filter(
            models.Productos.codigo_producto == codigo_producto
        ).first()

    def create(self, producto: schemas.ProductoCreate) -> models.Productos:
        # Verificar si el código de producto ya existe
        if self.get_by_codigo_producto(producto.codigo_producto):
            raise ValueError(f"El código de producto {producto.codigo_producto} ya existe")
        
        # Crear instancia
        db_producto = models.Productos(**producto.model_dump())
        
        self.db.add(db_producto)
        self.db.commit()
        self.db.refresh(db_producto)
        return db_producto

    def update(self, producto_id: int, producto_update: schemas.ProductoUpdate) -> Optional[models.Productos]:
        db_producto = self.get_by_id(producto_id)
        if not db_producto:
            return None
        
        update_data = producto_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_producto, field, value)
        
        self.db.commit()
        self.db.refresh(db_producto)
        return db_producto

    def partial_update(self, producto_id: int, producto_update: schemas.ProductoUpdate) -> Optional[models.Productos]:
        return self.update(producto_id, producto_update)

    def delete(self, producto_id: int) -> bool:
        db_producto = self.get_by_id(producto_id)
        if not db_producto:
            return False
        
        self.db.delete(db_producto)
        self.db.commit()
        return True

    def count_all(self) -> int:
        return self.db.query(models.Productos).count()


    def filtrar_por_categoria(self, categoria_id: int, skip: int = 0, limit: int = 100) -> List[models.Productos]:
        return self.db.query(models.Productos).filter(
            models.Productos.id_categoria == categoria_id
        ).offset(skip).limit(limit).all()

    def filtrar_por_distribuidor(self, distribuidor_id: int, skip: int = 0, limit: int = 100) -> List[models.Productos]:
        return self.db.query(models.Productos).filter(
            models.Productos.id_distribuidor == distribuidor_id
        ).offset(skip).limit(limit).all()