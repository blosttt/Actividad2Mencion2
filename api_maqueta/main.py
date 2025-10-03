from fastapi import FastAPI
import models
from database import engine
from routers import rest, graphql

# Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Productos - Sistema Vehicular",
    description="API REST y GraphQL para gestión de productos con filtros vehiculares",
    version="2.0.0"
)

# Incluir routers
app.include_router(rest.router)
app.include_router(graphql_router, prefix="/graphql")

@app.get("/")
async def root():
    return {
        "message": "API de Productos - Sistema Vehicular",
        "caracteristicas": {
            "base_datos": {
                "productos": "Código barras, nombre, descripción, marca, categoría, cantidad, precios",
                "categorias": "Sistema de categorías con tipos",
                "distribuidores": "Gestión de proveedores",
                "filtros_vehiculares": "Aceite, combustible, aire, polen"
            },
            "endpoints_rest": {
                "GET_ALL": "GET /productos/",
                "FILTROS_VEHICULOS": "GET /productos/filtrar-vehiculos",
                "GET_BY_ID": "GET /productos/{id}",
                "GET_BY_CODIGO_BARRAS": "GET /productos/codigo-barras/{codigo}",
                "POST": "POST /productos/ (Protegido con JWT)",
                "PUT": "PUT /productos/{id}",
                "PATCH": "PATCH /productos/{id}",
                "DELETE": "DELETE /productos/{id}"
            },
            "graphql": {
                "endpoint": "POST /graphql",
                "queries": ["products", "product", "productsByVehicleFilter", "categories"],
                "mutations": ["createProduct"]
            }
        },
        "autenticacion": {
            "metodo": "Bearer Token",
            "token": "secreto123"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "API Productos Vehiculares"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)