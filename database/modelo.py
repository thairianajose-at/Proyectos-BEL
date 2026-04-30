from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from datetime import datetime
from .config import Base, engine

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    rol = Column(String(20), default="admin")

class Logs(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    servicio = Column(String(50)) 
    fecha = Column(DateTime, default=datetime.now) 
    nivel = Column(String(20)) # INFO, WARNING, CRITICAL
    detalles = Column(JSON) 

class MetricasHistoricas(Base):
    __tablename__ = 'metricas_historicas'
    id = Column(Integer, primary_key=True)
    servicio = Column(String(50))
    cpu = Column(Float)
    ram = Column(Float)
    # nuevas metricas
    disco_lectura = Column(Float, default=0.0)
    disco_escritura = Column(Float, default=0.0)
    red_bajada = Column(Float, default=0.0)
    red_subida = Column(Float, default=0.0)
    fecha = Column(DateTime, default=datetime.now)

def crear_tablas():
    Base.metadata.create_all(bind=engine)