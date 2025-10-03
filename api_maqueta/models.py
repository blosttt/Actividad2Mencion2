from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# Tabla de categorías
class Categoria(Base):
    __tablename__ = "categorias"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, index=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo = Column(String(20), default="general")  # vehiculo, general, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    activo = Column(Integer, default=1)

# Tabla de distribuidores
class Distribuidor(Base):
    __tablename__ = "distribuidores"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    contacto = Column(String(100))
    telefono = Column(String(20))
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    activo = Column(Integer, default=1)

# Tabla principal de productos
class Producto(Base):
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo_barras = Column(String(50), unique=True, index=True, nullable=False)
    nombre = Column(String(100), index=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    marca = Column(String(50), nullable=False)
    
    # Relaciones
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    distribuidor_id = Column(Integer, ForeignKey("distribuidores.id"))
    
    # Campos de cantidad y precios
    cantidad = Column(Integer, default=0)
    precio_neto = Column(Float, nullable=False)
    porcentaje_ganancia = Column(Float, default=30.0)  # 30% por defecto
    iva = Column(Float, default=19.0)  # 19% IVA por defecto
    precio_venta = Column(Float, nullable=False)
    
    # Campos específicos para filtros de vehículos
    tipo_vehiculo = Column(String(20), nullable=True)  # auto, moto, camion
    tipo_aceite = Column(String(20), nullable=True)    # sintetico, mineral, semi-sintetico
    tipo_combustible = Column(String(20), nullable=True) # gasolina, diesel, electrico
    tipo_filtro = Column(String(20), nullable=True)    # aire, aceite, combustible, polen
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo = Column(Integer, default=1)
    
    # Relationships
    categoria = relationship("Categoria", backref="productos")
    distribuidor = relationship("Distribuidor", backref="productos")

    def calcular_precio_venta(self):
        """Calcula el precio de venta automáticamente"""
        ganancia = self.precio_neto * (self.porcentaje_ganancia / 100)
        iva_calculado = (self.precio_neto + ganancia) * (self.iva / 100)
        return self.precio_neto + ganancia + iva_calculado