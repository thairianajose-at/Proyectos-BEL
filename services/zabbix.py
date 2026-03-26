import random

SERVICIOS_EMPRESA = [
    {"nombre": "JAC Venezuela", "ip": "10.0.0.50", "url": "https://jacvenezuela.com/"},
    {"nombre": "Bel Motos", "ip": "10.0.0.51", "url": "https://belmotos.com/"},
    {"nombre": "IntraBel", "ip": "10.0.0.52", "url": "https://intrabel.com.ve/"},
]

def obtener_metricas_reales(nombre_servicio):
    servicio = next((s for s in SERVICIOS_EMPRESA if s["nombre"] == nombre_servicio), None)
    
    if not servicio:
        return {"error": "Servicio no encontrado"}

    
    return {
        "nombre": nombre_servicio,
        "ip": servicio["ip"],
        "cpu": random.randint(10, 100), 
        "ram": random.randint(20, 100),
        "red": random.randint(5, 100),
        "estado": "Online" if random.random() > 0.05 else "Offline"
    }