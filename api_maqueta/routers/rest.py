from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from services.product_service import ProductService
from services.category_service import CategoryService
from filters.vehicle_filters import VehicleFilter
import schemas

# Dependencia de autenticación
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    if credentials.credentials != "secreto123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    return True

# Dependencias de servicios
def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)

def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(db)

# Router principal
router = APIRouter(prefix="/productos", tags=["Productos"])

# Endpoints para productos
@router.get("/", response_model=schemas.ProductoListResponse)
async def get_all_productos(
    skip: int = 0,
    limit: int = 100,
    categoria_id: Optional[int] = Query(None),
    distribuidor_id: Optional[int] = Query(None),
    service: ProductService = Depends(get_product_service)
):
    """GET ALL - Obtener todos los productos con filtros opcionales"""
    if categoria_id:
        productos = service.filtrar_por_categoria(categoria_id, skip, limit)
        total = len(productos)  # Simplificado para el ejemplo
    elif distribuidor_id:
        productos = service.filtrar_por_distribuidor(distribuidor_id, skip, limit)
        total = len(productos)
    else:
        productos = service.get_all(skip=skip, limit=limit)
        total = service.count_all()
    
    return schemas.ProductoListResponse(
        items=productos,
        total=total,
        pagina=skip // limit + 1 if limit > 0 else 1,
        tamaño=limit
    )

@router.get("/filtros-vehiculos")
async def get_filtros_vehiculos():
    """Obtener los filtros disponibles para productos vehiculares"""
    return VehicleFilter.get_available_filters()

@router.get("/filtrar-vehiculos", response_model=schemas.ProductoListResponse)
async def filtrar_productos_vehiculares(
    tipo_vehiculo: Optional[str] = Query(None),
    tipo_aceite: Optional[str] = Query(None),
    tipo_combustible: Optional[str] = Query(None),
    tipo_filtro: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    service: ProductService = Depends(get_product_service)
):
    """Filtrar productos por características vehiculares"""
    # Validar filtros
    filtros = schemas.FiltroVehiculo(
        tipo_vehiculo=tipo_vehiculo,
        tipo_aceite=tipo_aceite,
        tipo_combustible=tipo_combustible,
        tipo_filtro=tipo_filtro
    )
    
    productos = service.filtrar_por_vehiculo(filtros, skip, limit)
    
    return schemas.ProductoListResponse(
        items=productos,
        total=len(productos),
        pagina=skip // limit + 1 if limit > 0 else 1,
        tamaño=limit
    )

@router.get("/{producto_id}", response_model=schemas.ProductoResponse)
async def get_producto_by_id(
    producto_id: int,
    service: ProductService = Depends(get_product_service)
):
    """GET by ID - Obtener un producto por su ID"""
    producto = service.get_by_id(producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.get("/codigo-barras/{codigo_barras}", response_model=schemas.ProductoResponse)
async def get_producto_by_codigo_barras(
    codigo_barras: str,
    service: ProductService = Depends(get_product_service)
):
    """GET by código de barras - Obtener un producto por su código de barras"""
    producto = service.get_by_codigo_barras(codigo_barras)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.post("/", response_model=schemas.ProductoResponse)
async def create_producto(
    producto: schemas.ProductoCreate,
    service: ProductService = Depends(get_product_service),
    token_valid: bool = Depends(verify_token)
):
    """POST - Crear un nuevo producto (Protegido con JWT)"""
    try:
        return service.create(producto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{producto_id}", response_model=schemas.ProductoResponse)
async def update_producto(
    producto_id: int,
    producto_update: schemas.ProductoUpdate,
    service: ProductService = Depends(get_product_service)
):
    """PUT - Actualizar completamente un producto"""
    producto_actualizado = service.update(producto_id, producto_update)
    if not producto_actualizado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto_actualizado

@router.patch("/{producto_id}", response_model=schemas.ProductoResponse)
async def partial_update_producto(
    producto_id: int,
    producto_update: schemas.ProductoUpdate,
    service: ProductService = Depends(get_product_service)
):
    """PATCH - Actualizar parcialmente un producto"""
    producto_actualizado = service.partial_update(producto_id, producto_update)
    if not producto_actualizado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto_actualizado

@router.delete("/{producto_id}")
async def delete_producto(
    producto_id: int,
    service: ProductService = Depends(get_product_service)
):
    """DELETE - Eliminar un producto (soft delete)"""
    if service.delete(producto_id):
        return {"message": "Producto eliminado correctamente"}
    else:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

# Endpoints para categorías
@router.get("/categorias/", response_model=List[schemas.CategoriaResponse])
async def get_categorias(
    tipo: Optional[str] = Query(None),
    service: CategoryService = Depends(get_category_service)
):
    """Obtener todas las categorías"""
    if tipo:
        return service.get_by_tipo(tipo)
    return service.get_all()