from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from urllib.parse import unquote
import uvicorn 
import requests
from controladores.crud import registrar_log, guardar_metrica_tiempo_real, obtener_indicadores_gerencia, obtener_logs_para_grafica
from services.lector_api import obtener_metricas_reales, SERVICIOS_EMPRESA
from database.config import SessionLocal

app = FastAPI()
URL_INFRA = "http://172.17.16.18:8000/api/containers"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "status": "Monitor de Infraestructura Bel Online",
        "servicios_disponibles": [s["nombre"] for s in SERVICIOS_EMPRESA]
    }

@app.post("/enviar-log")
def recibir_log(nivel: str, datos: dict):
    # Usamos el nombre del servicio desde los datos si viene, sino genérico
    servicio = datos.get("servicio", "General")
    res = registrar_log(servicio, nivel, datos)
    return {"message": "Log guardado", "id": res.id if res else 0}

@app.get("/metricas/{nombre_app}")
async def enviar_metricas_especificas(nombre_app: str):
    nombre_limpio = unquote(nombre_app)
    datos_finales = None
    
    try:
        res = requests.get(URL_INFRA, timeout=2)
        contenedores = res.json()
        match = next((c for c in contenedores if c.get("name") == nombre_limpio), None)
        
        if match:
            metrics = match.get("health", {}).get("metrics", {})
            datos_finales = {
                "nombre": nombre_limpio,
                "cpu": metrics.get("cpu_percent", 0),
                "ram": metrics.get("memory_percent", 0),
                "red": 10,
                "estado": "Online" if match.get("running") else "Offline"
            }
    except:
        datos_finales = obtener_metricas_reales(nombre_limpio)

    if datos_finales:
        # LOGICA AUTOMÁTICA DE ALERTAS Y REGISTRO
        if datos_finales["estado"] == "Offline":
            registrar_log(nombre_limpio, "CRITICAL", {"evento": "Servicio Caído"})
        
        if datos_finales["cpu"] > 85:
            registrar_log(nombre_limpio, "WARNING", {"evento": "CPU Crítico", "valor": datos_finales["cpu"]})

        # Guardar historial para gráficas
        guardar_metrica_tiempo_real(nombre_limpio, datos_finales["cpu"], datos_finales["ram"])
        
        # Inyectar indicadores de gerencia (Uptime e Incidencias)
        indicadores = obtener_indicadores_gerencia(nombre_limpio)
        datos_finales.update(indicadores)
        
        return datos_finales

    raise HTTPException(status_code=404, detail="Servicio no encontrado")

@app.get("/metricas-historicas/{nombre_app}")
def enviar_metricas_historicas(nombre_app: str):
    db = SessionLocal()
    try:
        nombre_limpio = unquote(nombre_app)
        logs = obtener_logs_para_grafica(db, nombre_limpio)
        return logs
    finally:
        db.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)