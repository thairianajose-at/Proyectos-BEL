from database.config import SessionLocal, engine
from database.modelo import Base, Usuario 

Base.metadata.create_all(bind=engine)

def insertar_usuarios_iniciales():
    db = SessionLocal()
    try:
        usuarios = [
            {"username": "admin", "password": "1234", "rol": "Administrador"},
            {"username": "wilder1", "password": "wilder1234", "rol": "Devops"},
            {"username": "ricardo", "password": "felizcumpleaños", "rol": "Devops"}
        ]

        for u in usuarios:
            existe = db.query(Usuario).filter(Usuario.username == u["username"]).first()
            if not existe:
                nuevo_usuario = Usuario(
                    username=u["username"],
                    password=u["pass"], 
                    rol=u["rol"]
                )
                db.add(nuevo_usuario)
        
        db.commit()
        print(" Usuarios de Corporación BEL insertados con éxito.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    insertar_usuarios_iniciales()