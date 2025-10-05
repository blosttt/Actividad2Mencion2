from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from service.product_service import ProductService
from service.category_service import CategoryService
import schemas
import models

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

# ==============================
# ROUTER PARA PRODUCTOS
# ==============================
router_productos = APIRouter(prefix="/productos", tags=["Productos"])

@router_productos.get("/", response_model=schemas.ProductoListResponse)
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
        total = len(productos)
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

@router_productos.get("/{producto_id}", response_model=schemas.ProductoResponse)
async def get_producto_by_id(
    producto_id: int,
    service: ProductService = Depends(get_product_service)
):
    """GET by ID - Obtener un producto por su ID"""
    producto = service.get_by_id(producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router_productos.get("/codigo-producto/{codigo_producto}", response_model=schemas.ProductoResponse)
async def get_producto_by_codigo_producto(
    codigo_producto: str,
    service: ProductService = Depends(get_product_service)
):
    """GET by código de producto - Obtener un producto por su código de producto"""
    producto = service.get_by_codigo_producto(codigo_producto)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router_productos.post("/", response_model=schemas.ProductoResponse)
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

@router_productos.put("/{producto_id}", response_model=schemas.ProductoResponse)
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

@router_productos.patch("/{producto_id}", response_model=schemas.ProductoResponse)
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

@router_productos.delete("/{producto_id}")
async def delete_producto(
    producto_id: int,
    service: ProductService = Depends(get_product_service)
):
    """DELETE - Eliminar un producto"""
    if service.delete(producto_id):
        return {"message": "Producto eliminado correctamente"}
    else:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

# ==============================
# ROUTER PARA CATEGORIAS
# ==============================
router_categorias = APIRouter(prefix="/categorias", tags=["Categorias"])

@router_categorias.get("/", response_model=List[schemas.CategoriaResponse])
async def get_all_categorias(service: CategoryService = Depends(get_category_service)):
    """GET ALL - Obtener todas las categorías"""
    return service.get_all()

@router_categorias.get("/{categoria_id}", response_model=schemas.CategoriaResponse)
async def get_categoria_by_id(
    categoria_id: int, 
    service: CategoryService = Depends(get_category_service)
):
    """GET by ID - Obtener una categoría por su ID"""
    categoria = service.get_by_id(categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

@router_categorias.post("/", response_model=schemas.CategoriaResponse, dependencies=[Depends(verify_token)])
async def create_categoria(
    categoria: schemas.CategoriaCreate, 
    service: CategoryService = Depends(get_category_service)
):
    """POST - Crear una nueva categoría (Protegido con JWT)"""
    try:
        return service.create(categoria)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router_categorias.put("/{categoria_id}", response_model=schemas.CategoriaResponse)
async def update_categoria(
    categoria_id: int, 
    categoria_update: schemas.CategoriaCreate, 
    service: CategoryService = Depends(get_category_service)
):
    """PUT - Actualizar completamente una categoría"""
    updated = service.update(categoria_id, categoria_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return updated

@router_categorias.patch("/{categoria_id}", response_model=schemas.CategoriaResponse)
async def partial_update_categoria(
    categoria_id: int, 
    categoria_update: schemas.CategoriaUpdate, 
    service: CategoryService = Depends(get_category_service)
):
    """PATCH - Actualizar parcialmente una categoría"""
    updated = service.partial_update(categoria_id, categoria_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return updated

@router_categorias.delete("/{categoria_id}")
async def delete_categoria(
    categoria_id: int, 
    service: CategoryService = Depends(get_category_service)
):
    """DELETE - Eliminar una categoría"""
    if service.delete(categoria_id):
        return {"message": "Categoría eliminada correctamente"}
    else:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

# ==============================
# ROUTER PARA DISTRIBUIDORES
# ==============================
router_distribuidores = APIRouter(prefix="/distribuidores", tags=["Distribuidores"])

@router_distribuidores.get("/", response_model=List[schemas.DistribuidorResponse])
async def get_all_distribuidores(db: Session = Depends(get_db)):
    """GET ALL - Obtener todos los distribuidores"""
    return db.query(models.Distribuidores).all()

@router_distribuidores.get("/{distribuidor_id}", response_model=schemas.DistribuidorResponse)
async def get_distribuidor_by_id(distribuidor_id: int, db: Session = Depends(get_db)):
    """GET by ID - Obtener un distribuidor por su ID"""
    distribuidor = db.query(models.Distribuidores).filter(models.Distribuidores.id_distribuidor == distribuidor_id).first()
    if not distribuidor:
        raise HTTPException(status_code=404, detail="Distribuidor no encontrado")
    return distribuidor

@router_distribuidores.get("/rut/{rut}", response_model=schemas.DistribuidorResponse)
async def get_distribuidor_by_rut(rut: str, db: Session = Depends(get_db)):
    """GET by RUT - Obtener un distribuidor por su RUT"""
    distribuidor = db.query(models.Distribuidores).filter(models.Distribuidores.rut == rut).first()
    if not distribuidor:
        raise HTTPException(status_code=404, detail="Distribuidor no encontrado")
    return distribuidor

@router_distribuidores.post("/", response_model=schemas.DistribuidorResponse, dependencies=[Depends(verify_token)])
async def create_distribuidor(
    distribuidor: schemas.DistribuidorCreate, 
    db: Session = Depends(get_db)
):
    """POST - Crear un nuevo distribuidor (Protegido con JWT)"""
    try:
        db_distribuidor = models.Distribuidores(**distribuidor.dict())
        db.add(db_distribuidor)
        db.commit()
        db.refresh(db_distribuidor)
        return db_distribuidor
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al crear distribuidor: {str(e)}")

@router_distribuidores.put("/{distribuidor_id}", response_model=schemas.DistribuidorResponse)
async def update_distribuidor(
    distribuidor_id: int, 
    distribuidor_update: schemas.DistribuidorCreate, 
    db: Session = Depends(get_db)
):
    """PUT - Actualizar completamente un distribuidor"""
    distribuidor = db.query(models.Distribuidores).filter(models.Distribuidores.id_distribuidor == distribuidor_id).first()
    if not distribuidor:
        raise HTTPException(status_code=404, detail="Distribuidor no encontrado")
    
    for key, value in distribuidor_update.dict().items():
        setattr(distribuidor, key, value)
    
    db.commit()
    db.refresh(distribuidor)
    return distribuidor

@router_distribuidores.patch("/{distribuidor_id}", response_model=schemas.DistribuidorResponse)
async def partial_update_distribuidor(
    distribuidor_id: int, 
    distribuidor_update: schemas.DistribuidorUpdate, 
    db: Session = Depends(get_db)
):
    """PATCH - Actualizar parcialmente un distribuidor"""
    distribuidor = db.query(models.Distribuidores).filter(models.Distribuidores.id_distribuidor == distribuidor_id).first()
    if not distribuidor:
        raise HTTPException(status_code=404, detail="Distribuidor no encontrado")
    
    update_data = distribuidor_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(distribuidor, key, value)
    
    db.commit()
    db.refresh(distribuidor)
    return distribuidor

@router_distribuidores.delete("/{distribuidor_id}")
async def delete_distribuidor(distribuidor_id: int, db: Session = Depends(get_db)):
    """DELETE - Eliminar un distribuidor"""
    distribuidor = db.query(models.Distribuidores).filter(models.Distribuidores.id_distribuidor == distribuidor_id).first()
    if not distribuidor:
        raise HTTPException(status_code=404, detail="Distribuidor no encontrado")
    
    db.delete(distribuidor)
    db.commit()
    return {"message": "Distribuidor eliminado correctamente"}