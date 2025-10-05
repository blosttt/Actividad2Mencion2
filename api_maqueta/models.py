from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Date, DECIMAL, Computed
from sqlalchemy.orm import relationship
from datetime import datetime, date
from database import Base

# ==============================
# TABLA DISTRIBUIDORES
# ==============================
class Distribuidores(Base):
    __tablename__ = "Distribuidores"
    
    id_distribuidor = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    rut = Column(String(15), unique=True, nullable=False)
    telefono = Column(String(20))
    email = Column(String(100))
    direccion = Column(String(150))
    ciudad = Column(String(50))
    
    # Relationships
    productos = relationship("Productos", back_populates="distribuidor")

# ==============================
# TABLA CATEGORIAS
# ==============================
class Categorias(Base):
    __tablename__ = "Categorias"
    
    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre_categoria = Column(String(50), unique=True, nullable=False)  # Ej: Aire, Aceite, Combustible, Habitáculo
    
    # Relationships
    productos = relationship("Productos", back_populates="categoria")

# ==============================
# TABLA PRODUCTOS
# ==============================
class Productos(Base):
    __tablename__ = "Productos"
    
    id_producto = Column(Integer, primary_key=True, index=True)
    codigo_producto = Column(String(50), unique=True, nullable=False)
    nombre_producto = Column(String(100), nullable=False)
    id_categoria = Column(Integer, ForeignKey("Categorias.id_categoria"), nullable=False)
    marca = Column(String(50), nullable=False)
    descripcion = Column(Text)
    
    # PRECIOS
    precio_compra = Column(DECIMAL(10, 2), nullable=False)  # Costo del distribuidor
    margen_ganancia = Column(DECIMAL(5, 2), default=30)  # % de ganancia
    precio_neto = Column(DECIMAL(10, 2), Computed("precio_compra + (precio_compra * margen_ganancia / 100)"))
    precio_iva = Column(DECIMAL(10, 2), Computed("precio_neto + (precio_neto * 0.19)"))
    precio_venta = Column(DECIMAL(10, 2), Computed("ROUND(precio_iva, 0)"))
    
    # STOCK Y PROVEEDOR
    stock = Column(Integer, default=0)
    id_distribuidor = Column(Integer, ForeignKey("Distribuidores.id_distribuidor"))
    fecha_actualizacion = Column(Date, default=date.today)
    
    # Relationships
    categoria = relationship("Categorias", back_populates="productos")
    distribuidor = relationship("Distribuidores", back_populates="productos")