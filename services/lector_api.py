import requests
import random
from database.config import SessionLocal 
from database.modelo import Logs        

SERVICIOS_EMPRESA = [
    {"nombre": "JAC Venezuela", "ip": "158.69.105.179", "url": "https://jacvenezuela.com/"},
    {"nombre": "Bel Motos", "ip": "142.4.197.233", "url": "https://belmotos.com/"},
    {"nombre": "IntraBel", "ip": "10.0.0.52", "url": "https://intrabel.com.ve/"},
    {"nombre": "bel.com", "ip":"167.114.200.164", "url":"https://www.bel.com/"}
]

def obtener_metricas_reales(nombre_servicio):
  
    return {
        "nombre": nombre_servicio,
        "cpu": random.randint(15, 45), 
        "ram": random.randint(20, 50),
        "dl": round(random.uniform(0.1, 5.0), 1),
        "de": round(random.uniform(0.1, 2.0), 1),
        "red": random.randint(5, 15),
        "estado": "Online",
        "uptime": "99.9%",
        "incidencias": 0
    }