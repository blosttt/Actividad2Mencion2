import strawberry
from typing import List, Optional
from strawberry.fastapi import GraphQLRouter
from sqlalchemy.orm import Session
from fastapi import Depends

from database import get_db
from service.product_service import ProductService
from service.category_service import CategoryService
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
    id_categoria: int
    nombre_categoria: str

    @classmethod
    def from_db(cls, db_categoria: models.Categorias):
        return cls(
            id_categoria=db_categoria.id_categoria,
            nombre_categoria=db_categoria.nombre_categoria
        )

@strawberry.type
class Distribuidor:
    id_distribuidor: int
    nombre: str
    rut: str
    telefono: Optional[str]
    email: Optional[str]
    direccion: Optional[str]
    ciudad: Optional[str]

    @classmethod
    def from_db(cls, db_distribuidor: models.Distribuidores):
        return cls(
            id_distribuidor=db_distribuidor.id_distribuidor,
            nombre=db_distribuidor.nombre,
            rut=db_distribuidor.rut,
            telefono=db_distribuidor.telefono,
            email=db_distribuidor.email,
            direccion=db_distribuidor.direccion,
            ciudad=db_distribuidor.ciudad
        )

@strawberry.type
class Product:
    id_producto: int
    codigo_producto: str
    nombre_producto: str
    marca: str
    descripcion: Optional[str]
    precio_compra: float
    margen_ganancia: float
    precio_neto: float
    iva: float
    precio_venta: float
    stock: int
    fecha_actualizacion: str
    categoria: Optional[Categoria]
    distribuidor: Optional[Distribuidor]

    @classmethod
    def from_db(cls, db_producto: models.Productos):
        return cls(
            id_producto=db_producto.id_producto,
            codigo_producto=db_producto.codigo_producto,
            nombre_producto=db_producto.nombre_producto,
            marca=db_producto.marca,
            descripcion=db_producto.descripcion,
            precio_compra=float(db_producto.precio_compra),
            margen_ganancia=float(db_producto.margen_ganancia),
            precio_neto=float(db_producto.precio_neto),
            iva=float(db_producto.iva),
            precio_venta=float(db_producto.precio_venta),
            stock=db_producto.stock,
            fecha_actualizacion=str(db_producto.fecha_actualizacion),
            categoria=Categoria.from_db(db_producto.categoria) if db_producto.categoria else None,
            distribuidor=Distribuidor.from_db(db_producto.distribuidor) if db_producto.distribuidor else None
        )

# Inputs GraphQL
@strawberry.input
class ProductInput:
    codigo_producto: str
    nombre_producto: str
    id_categoria: int
    marca: str
    descripcion: Optional[str] = None
    precio_compra: float
    margen_ganancia: float = 30.0
    stock: int = 0
    id_distribuidor: Optional[int] = None

@strawberry.input
class CategoriaInput:
    nombre_categoria: str

@strawberry.input
class DistribuidorInput:
    nombre: str
    rut: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None

# Queries GraphQL
@strawberry.type
class Query:
    @strawberry.field
    def products(self, info, skip: int = 0, limit: int = 100) -> List[Product]:
        """Query products - Obtener lista de productos"""
        service = info.context["product_service"]
        db_productos = service.get_all(skip=skip, limit=limit)
        return [Product.from_db(producto) for producto in db_productos]
    
    @strawberry.field
    def product(self, info, id: int) -> Optional[Product]:
        """Query product - Obtener un producto por ID"""
        service = info.context["product_service"]
        db_producto = service.get_by_id(id)
        return Product.from_db(db_producto) if db_producto else None
    
    @strawberry.field
    def categories(self, info) -> List[Categoria]:
        """Query categories - Obtener todas las categorías"""
        service = info.context["category_service"]
        db_categorias = service.get_all()
        return [Categoria.from_db(categoria) for categoria in db_categorias]

    @strawberry.field
    def distribuidores(self, info) -> List[Distribuidor]:
        """Query distribuidores - Obtener todos los distribuidores"""
        db = info.context["db"]
        db_distribuidores = db.query(models.Distribuidores).all()
        return [Distribuidor.from_db(distribuidor) for distribuidor in db_distribuidores]

# Mutations GraphQL
@strawberry.type
class Mutation:
    @strawberry.mutation
    def createProduct(self, info, product: ProductInput) -> Product:
        """Mutation createProduct - Crear un nuevo producto"""
        service = info.context["product_service"]
        
        producto_data = schemas.ProductoCreate(
            codigo_producto=product.codigo_producto,
            nombre_producto=product.nombre_producto,
            id_categoria=product.id_categoria,
            marca=product.marca,
            descripcion=product.descripcion,
            precio_compra=product.precio_compra,
            margen_ganancia=product.margen_ganancia,
            stock=product.stock,
            id_distribuidor=product.id_distribuidor
        )
        
        try:
            db_producto = service.create(producto_data)
            return Product.from_db(db_producto)
        except ValueError as e:
            raise Exception(str(e))

    @strawberry.mutation
    def createCategoria(self, info, categoria: CategoriaInput) -> Categoria:
        """Mutation createCategoria - Crear una nueva categoría"""
        service = info.context["category_service"]
        
        categoria_data = schemas.CategoriaCreate(
            nombre_categoria=categoria.nombre_categoria
        )
        
        try:
            db_categoria = service.create(categoria_data)
            return Categoria.from_db(db_categoria)
        except ValueError as e:
            raise Exception(str(e))

    @strawberry.mutation
    def createDistribuidor(self, info, distribuidor: DistribuidorInput) -> Distribuidor:
        """Mutation createDistribuidor - Crear un nuevo distribuidor"""
        db = info.context["db"]
        
        distribuidor_data = schemas.DistribuidorCreate(
            nombre=distribuidor.nombre,
            rut=distribuidor.rut,
            telefono=distribuidor.telefono,
            email=distribuidor.email,
            direccion=distribuidor.direccion,
            ciudad=distribuidor.ciudad
        )
        
        try:
            db_distribuidor = models.Distribuidores(**distribuidor_data.dict())
            db.add(db_distribuidor)
            db.commit()
            db.refresh(db_distribuidor)
            return Distribuidor.from_db(db_distribuidor)
        except Exception as e:
            db.rollback()
            raise Exception(f"Error al crear distribuidor: {str(e)}")

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_router = GraphQLRouter(schema, context_getter=get_context)