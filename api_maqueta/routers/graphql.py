import strawberry
from typing import List, Optional
from strawberry.fastapi import GraphQLRouter
from sqlalchemy.orm import Session
from fastapi import Depends

from database import get_db
from services.product_service import ProductService
from services.category_service import CategoryService
import models
import schemas

# Context dependency
async def get_context(db: Session = Depends(get_db)):
    return {
        "db": db, 
        "product_service": ProductService(db),
        "category_service": CategoryService(db)
    }

# Tipos GraphQL
@strawberry.type
class Categoria:
    id: int
    nombre: str
    descripcion: Optional[str]
    tipo: str

    @classmethod
    def from_db(cls, db_categoria: models.Categoria):
        return cls(
            id=db_categoria.id,
            nombre=db_categoria.nombre,
            descripcion=db_categoria.descripcion,
            tipo=db_categoria.tipo
        )

@strawberry.type
class Producto:
    id: int
    codigo_barras: str
    nombre: str
    descripcion: Optional[str]
    marca: str
    cantidad: int
    precio_neto: float
    porcentaje_ganancia: float
    iva: float
    precio_venta: float
    tipo_vehiculo: Optional[str]
    tipo_aceite: Optional[str]
    tipo_combustible: Optional[str]
    tipo_filtro: Optional[str]
    categoria: Optional[Categoria]

    @classmethod
    def from_db(cls, db_producto: models.Producto):
        return cls(
            id=db_producto.id,
            codigo_barras=db_producto.codigo_barras,
            nombre=db_producto.nombre,
            descripcion=db_producto.descripcion,
            marca=db_producto.marca,
            cantidad=db_producto.cantidad,
            precio_neto=db_producto.precio_neto,
            porcentaje_ganancia=db_producto.porcentaje_ganancia,
            iva=db_producto.iva,
            precio_venta=db_producto.precio_venta,
            tipo_vehiculo=db_producto.tipo_vehiculo,
            tipo_aceite=db_producto.tipo_aceite,
            tipo_combustible=db_producto.tipo_combustible,
            tipo_filtro=db_producto.tipo_filtro,
            categoria=Categoria.from_db(db_producto.categoria) if db_producto.categoria else None
        )

# Inputs GraphQL
@strawberry.input
class ProductoInput:
    codigo_barras: str
    nombre: str
    descripcion: Optional[str] = None
    marca: str
    categoria_id: int
    cantidad: int = 0
    precio_neto: float
    porcentaje_ganancia: float = 30.0
    iva: float = 19.0
    tipo_vehiculo: Optional[str] = None
    tipo_aceite: Optional[str] = None
    tipo_combustible: Optional[str] = None
    tipo_filtro: Optional[str] = None

@strawberry.input
class FiltroVehiculoInput:
    tipo_vehiculo: Optional[str] = None
    tipo_aceite: Optional[str] = None
    tipo_combustible: Optional[str] = None
    tipo_filtro: Optional[str] = None

# Queries GraphQL
@strawberry.type
class Query:
    @strawberry.field
    def products(self, info, skip: int = 0, limit: int = 100) -> List[Producto]:
        """Query products - Obtener lista de productos"""
        service = info.context["product_service"]
        db_productos = service.get_all(skip=skip, limit=limit)
        return [Producto.from_db(producto) for producto in db_productos]
    
    @strawberry.field
    def product(self, info, id: int) -> Optional[Producto]:
        """Query product - Obtener un producto por ID"""
        service = info.context["product_service"]
        db_producto = service.get_by_id(id)
        return Producto.from_db(db_producto) if db_producto else None
    
    @strawberry.field
    def productsByVehicleFilter(self, info, filtros: FiltroVehiculoInput) -> List[Producto]:
        """Query productsByVehicleFilter - Filtrar productos vehiculares"""
        service = info.context["product_service"]
        
        filtro_schema = schemas.FiltroVehiculo(
            tipo_vehiculo=filtros.tipo_vehiculo,
            tipo_aceite=filtros.tipo_aceite,
            tipo_combustible=filtros.tipo_combustible,
            tipo_filtro=filtros.tipo_filtro
        )
        
        db_productos = service.filtrar_por_vehiculo(filtro_schema)
        return [Producto.from_db(producto) for producto in db_productos]
    
    @strawberry.field
    def categories(self, info) -> List[Categoria]:
        """Query categories - Obtener todas las categorías"""
        service = info.context["category_service"]
        db_categorias = service.get_all()
        return [Categoria.from_db(categoria) for categoria in db_categorias]

# Mutations GraphQL
@strawberry.type
class Mutation:
    @strawberry.mutation
    def createProduct(self, info, producto: ProductoInput) -> Producto:
        """Mutation createProduct - Crear un nuevo producto"""
        service = info.context["product_service"]
        
        producto_data = schemas.ProductoCreate(
            codigo_barras=producto.codigo_barras,
            nombre=producto.nombre,
            descripcion=producto.descripcion,
            marca=producto.marca,
            categoria_id=producto.categoria_id,
            cantidad=producto.cantidad,
            precio_neto=producto.precio_neto,
            porcentaje_ganancia=producto.porcentaje_ganancia,
            iva=producto.iva,
            tipo_vehiculo=producto.tipo_vehiculo,
            tipo_aceite=producto.tipo_aceite,
            tipo_combustible=producto.tipo_combustible,
            tipo_filtro=producto.tipo_filtro
        )
        
        try:
            db_producto = service.create(producto_data)
            return Producto.from_db(db_producto)
        except ValueError as e:
            raise Exception(str(e))

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_router = GraphQLRouter(schema, context_getter=get_context)