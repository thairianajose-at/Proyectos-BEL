from database.config import SessionLocal
from database.modelo import Logs, Usuario, MetricasHistoricas
from sqlalchemy import func
from datetime import datetime, timedelta

def registrar_log(servicio, nivel, datos_dict):
    db = SessionLocal()
    try:
        nuevo_log = Logs(servicio=servicio, nivel=nivel, detalles=datos_dict)
        db.add(nuevo_log) 
        db.commit()
        db.refresh(nuevo_log)
        return nuevo_log
    except Exception as e:
        db.rollback()
        print(f"Error al registrar log: {e}")
        return None
    finally:
        db.close()

def guardar_metrica_tiempo_real(servicio, cpu, ram):
    db = SessionLocal()
    try:
        nueva_m = MetricasHistoricas(servicio=servicio, cpu=cpu, ram=ram)
        db.add(nueva_m)
        db.commit()
    except Exception as e:
        print(f"Error al guardar métrica: {e}")
    finally:
        db.close()

def obtener_indicadores_gerencia(nombre_servicio):
    db = SessionLocal()
    try:
        hace_24h = datetime.now() - timedelta(hours=24)
        caidas = db.query(Logs).filter(
            Logs.servicio == nombre_servicio, 
            Logs.nivel == "CRITICAL",
            Logs.fecha >= hace_24h
        ).count()
        uptime = max(0, 100 - (caidas * 0.1)) # Penalización por caída
        return {"uptime": uptime, "incidencias": caidas}
    except Exception as e:
        print(f"Error en indicadores: {e}")
        return {"uptime": 100, "incidencias": 0}
    finally:
        db.close()

def obtener_logs_para_grafica(db_session, nombre_servicio):
    try:
        stats = db_session.query(
            Logs.nivel, 
            func.count(Logs.id).label("total")
        ).filter(Logs.servicio == nombre_servicio).group_by(Logs.nivel).all()
        return {s.nivel: s.total for s in stats}
    except Exception as e:
        print(f"Error en consulta de gráfica: {e}")
        return {}

def crear_usuario(username, password, rol="admin"):
    db = SessionLocal()
    try:
        existe = db.query(Usuario).filter(Usuario.username == username).first()
        if existe: return None
        nuevo_usuario = Usuario(username=username, password=password, rol=rol)
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario
    except Exception as e:
        db.rollback()
        return None
    finally:
        db.close()

def validar_usuario(username, password):
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(
            Usuario.username == username, 
            Usuario.password == password
        ).first()
        if user:
            return {"id": user.id, "username": user.username, "rol": user.rol}
        return None
    except Exception as e:
        return None
    finally:
        db.close()