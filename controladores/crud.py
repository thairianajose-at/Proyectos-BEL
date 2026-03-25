from database.config import SessionLocal
from database.modelo import Logs, Usuario
from sqlalchemy import func

def registrar_log(servicio, nivel, datos_dict):
    """Registra un evento vinculado a un servicio específico."""
    db = SessionLocal()
    try:
        # Añadimos el campo 'servicio' para que la API pueda filtrar luego
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

# --- ESTA ES LA FUNCIÓN QUE SOLUCIONA EL ERROR DE LA API ---
def obtener_logs_para_grafica(db_session, nombre_servicio):
    """
    Consulta la base de datos para contar cuántos logs hay de cada nivel
    (INFO, WARNING, CRITICAL) para un servicio dado.
    """
    try:
        stats = db_session.query(
            Logs.nivel, 
            func.count(Logs.id).label("total")
        ).filter(Logs.servicio == nombre_servicio).group_by(Logs.nivel).all()
        
        # Lo convertimos a un diccionario simple para la API
        return {s.nivel: s.total for s in stats}
    except Exception as e:
        print(f"Error en consulta de gráfica: {e}")
        return {}

def crear_usuario(username, password, rol="admin"):
    db = SessionLocal()
    try:
        existe = db.query(Usuario).filter(Usuario.username == username).first()
        if existe:
            return None
            
        nuevo_usuario = Usuario(username=username, password=password, rol=rol)
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario
    except Exception as e:
        db.rollback()
        print(f"Error al crear usuario: {e}")
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
            return {
                "id": user.id,
                "username": user.username,
                "rol": user.rol
            }
        return None
    except Exception as e:
        print(f"Error en validación: {e}")
        return None
    finally:
        db.close()