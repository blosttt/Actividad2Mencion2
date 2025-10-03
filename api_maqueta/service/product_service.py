from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict
import models
import schemas

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[models.Producto]:
        return self.db.query(models.Producto).filter(
            models.Producto.activo == 1
        ).offset(skip).limit(limit).all()

    def get_by_id(self, producto_id: int) -> Optional[models.Producto]:
        return self.db.query(models.Producto).filter(
            and_(
                models.Producto.id == producto_id,
                models.Producto.activo == 1
            )
        ).first()

    def get_by_codigo_barras(self, codigo_barras: str) -> Optional[models.Producto]:
        return self.db.query(models.Producto).filter(
            and_(
                models.Producto.codigo_barras == codigo_barras,
                models.Producto.activo == 1
            )
        ).first()

    def create(self, producto: schemas.ProductoCreate) -> models.Producto:
        # Verificar si el código de barras ya existe
        if self.get_by_codigo_barras(producto.codigo_barras):
            raise ValueError(f"El código de barras {producto.codigo_barras} ya existe")
        
        # Crear instancia y calcular precio de venta
        db_producto = models.Producto(**producto.model_dump())
        db_producto.precio_venta = db_producto.calcular_precio_venta()
        
        self.db.add(db_producto)
        self.db.commit()
        self.db.refresh(db_producto)
        return db_producto

    def update(self, producto_id: int, producto_update: schemas.ProductoUpdate) -> Optional[models.Producto]:
        db_producto = self.get_by_id(producto_id)
        if not db_producto:
            return None
        
        update_data = producto_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_producto, field, value)
        
        # Recalcular precio de venta si cambió precio_neto, porcentaje_ganancia o iva
        if any(field in update_data for field in ['precio_neto', 'porcentaje_ganancia', 'iva']):
            db_producto.precio_venta = db_producto.calcular_precio_venta()
        
        self.db.commit()
        self.db.refresh(db_producto)
        return db_producto

    def partial_update(self, producto_id: int, producto_update: schemas.ProductoUpdate) -> Optional[models.Producto]:
        return self.update(producto_id, producto_update)

    def delete(self, producto_id: int) -> bool:
        db_producto = self.get_by_id(producto_id)
        if not db_producto:
            return False
        
        db_producto.activo = 0
        self.db.commit()
        return True

    def count_all(self) -> int:
        return self.db.query(models.Producto).filter(
            models.Producto.activo == 1
        ).count()

    # Filtros específicos para productos vehiculares
    def filtrar_por_vehiculo(self, filtros: schemas.FiltroVehiculo, skip: int = 0, limit: int = 100) -> List[models.Producto]:
        query = self.db.query(models.Producto).filter(
            models.Producto.activo == 1
        )
        
        # Aplicar filtros si están presentes
        if filtros.tipo_vehiculo:
            query = query.filter(models.Producto.tipo_vehiculo == filtros.tipo_vehiculo)
        if filtros.tipo_aceite:
            query = query.filter(models.Producto.tipo_aceite == filtros.tipo_aceite)
        if filtros.tipo_combustible:
            query = query.filter(models.Producto.tipo_combustible == filtros.tipo_combustible)
        if filtros.tipo_filtro:
            query = query.filter(models.Producto.tipo_filtro == filtros.tipo_filtro)
        
        return query.offset(skip).limit(limit).all()

    def filtrar_por_categoria(self, categoria_id: int, skip: int = 0, limit: int = 100) -> List[models.Producto]:
        return self.db.query(models.Producto).filter(
            and_(
                models.Producto.categoria_id == categoria_id,
                models.Producto.activo == 1
            )
        ).offset(skip).limit(limit).all()

    def filtrar_por_distribuidor(self, distribuidor_id: int, skip: int = 0, limit: int = 100) -> List[models.Producto]:
        return self.db.query(models.Producto).filter(
            and_(
                models.Producto.distribuidor_id == distribuidor_id,
                models.Producto.activo == 1
            )
        ).offset(skip).limit(limit).all()