from fastapi import FastAPI
import models
from database import engine
from routers import rest, graphql
from routers.graphql import graphql_router

# Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Productos - Sistema Vehicular",
    description="API REST y GraphQL para gestión de productos vehiculares",
    version="2.0.0"
)

# Incluir routers
app.include_router(rest.router_productos)
app.include_router(rest.router_categorias)
app.include_router(rest.router_distribuidores)
app.include_router(graphql_router, prefix="/graphql")

@app.get("/")
async def root():
    return {
        "message": "API de Productos - Sistema Vehicular",
        "caracteristicas": {
            "base_datos": {
                "productos": "Código producto, nombre, descripción, marca, categoría, precios calculados",
                "categorias": "Sistema de categorías (Aire, Aceite, Combustible, Habitáculo)",
                "distribuidores": "Gestión de proveedores con RUT, dirección, ciudad"
            },
            "endpoints_rest": {
                "productos": {
                    "GET_ALL": "GET /productos/",
                    "GET_BY_ID": "GET /productos/{producto_id}",
                    "GET_BY_CODIGO": "GET /productos/codigo-producto/{codigo_producto}",
                    "POST": "POST /productos/ (Protegido con JWT)",
                    "PUT": "PUT /productos/{producto_id}",
                    "PATCH": "PATCH /productos/{producto_id}",
                    "DELETE": "DELETE /productos/{producto_id}"
                },
                "categorias": {
                    "GET_ALL": "GET /categorias/",
                    "GET_BY_ID": "GET /categorias/{categoria_id}",
                    "POST": "POST /categorias/ (Protegido con JWT)",
                    "PUT": "PUT /categorias/{categoria_id}",
                    "PATCH": "PATCH /categorias/{categoria_id}",
                    "DELETE": "DELETE /categorias/{categoria_id}"
                },
                "distribuidores": {
                    "GET_ALL": "GET /distribuidores/",
                    "GET_BY_ID": "GET /distribuidores/{distribuidor_id}",
                    "GET_BY_RUT": "GET /distribuidores/rut/{rut}",
                    "POST": "POST /distribuidores/ (Protegido con JWT)",
                    "PUT": "PUT /distribuidores/{distribuidor_id}",
                    "PATCH": "PATCH /distribuidores/{distribuidor_id}",
                    "DELETE": "DELETE /distribuidores/{distribuidor_id}"
                }
            },
            "graphql": {
                "endpoint": "POST /graphql",
                "queries": ["products", "product", "categories", "distribuidores"],
                "mutations": ["createProduct", "createCategoria", "createDistribuidor"]
            }
        },
        "autenticacion": {
            "metodo": "Bearer Token",
            "token": "secreto123"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "API Productos Vehiculos"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)