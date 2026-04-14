import requests
import random

# CONFIGURACIÓN PARA LA EMPRESA
MODO_OFFLINE = False 
API_URL_REAL = "http://127.0.0.1:8000/metricas/"

def obtener_metricas_reales(servicio_obj):
    if isinstance(servicio_obj, str):
        id_tecnico = servicio_obj
        nombre_display = servicio_obj
    else:
        # Usamos el container_id para la consulta técnica y nombre para la UI
        id_tecnico = servicio_obj.get("container_id", "unknown")
        nombre_display = servicio_obj.get("nombre", "Desconocido")

    if MODO_OFFLINE:
        return {
            "nombre": nombre_display,
            "cpu": random.randint(10, 30),
            "ram": random.randint(15, 45),
            "dl": random.randint(1, 10), # Disco Lectura
            "de": random.randint(1, 10), # Disco Escritura
            "red": random.randint(5, 20),
            "estado": "Online"
        }

    try:
        # Llamada a nuestra API local de FastAPI
        res = requests.get(f"{API_URL_REAL}{id_tecnico}", timeout=2.0)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f"Error en lector_api: {e}")
    
    # Fallback si la comunicación falla
    return {
        "nombre": nombre_display, 
        "cpu": 0, "ram": 0, "dl": 0, "de": 0, "red": 0, 
        "estado": "Error Link"
    }