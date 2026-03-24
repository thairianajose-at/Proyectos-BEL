from database.config import SessionLocal
from database.modelo import Logs, Usuario

def registrar_log(nivel, datos_dict):
    db = SessionLocal()
    try:
        nuevo_log = Logs(nivel=nivel, detalles=datos_dict)
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
    """
    Valida las credenciales. 
    IMPORTANTE: No cerramos la sesión ANTES de retornar el objeto 
    o usamos una técnica para mantener los datos en memoria.
    """
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