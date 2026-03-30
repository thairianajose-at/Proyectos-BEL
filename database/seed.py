from database.config import SessionLocal
from database.modelo import Usuario
from controladores.crud import crear_usuario

def ejecutar_seed():
    db = SessionLocal()
    try:
        # veo si la tabla de usuarios está vacía para no duplicar datos
        if not db.query(Usuario).first():
            # Usuario Administrador (Acceso Técnico Total)
            crear_usuario("Yulimar", "admin123", rol="admin")
            # Usuario DevOps
            crear_usuario("Wilder", "wilder1234", rol="admin")
            # Usuario Gerencia Para visualización de métricas
            crear_usuario("Mixyeli", "bel2026", rol="gerencia")
            crear_usuario("Javier", "bel2026", rol="gerencia")
            crear_usuario("Merwin", "corpobel13", rol="admin")
            crear_usuario("Ricardo", "corpobel", rol="admin")


    except Exception as e:
        print(f"Error al inicializar datos (Seed): {e}")
    finally:
        db.close()