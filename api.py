from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from urllib.parse import unquote
import uvicorn 
import requests
from controladores.crud import registrar_log, guardar_metrica_tiempo_real, obtener_indicadores_gerencia, obtener_logs_para_grafica
from services.lector_api import obtener_metricas_reales, SERVICIOS_EMPRESA
from database.config import SessionLocal

app = FastAPI()

# IP Real
URL_INFRA_REAL = "http://172.17.16.18:8000/api/containers" 

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
        "status": "Monitor de Infraestructura Bel Online - Híbrido",
        "servicios": [s["nombre"] for s in SERVICIOS_EMPRESA]
    }

@app.get("/metricas/{nombre_app}")
async def enviar_metricas_especificas(nombre_app: str):
    nombre_limpio = unquote(nombre_app)
    datos_finales = None
    
    # logica de resilencia
    try:
        # Intentamos conexión directa 
        res = requests.get(URL_INFRA_REAL, timeout=2.0)
        contenedores = res.json()
        match = next((c for c in contenedores if c.get("name") == nombre_limpio), None)
        
        if match:
            m = match.get("health", {}).get("metrics", {})
            running = match.get("running", False)
            datos_finales = {
                "nombre": nombre_limpio,
                "cpu": round(m.get("cpu_percent", 0), 1),
                "ram": round(m.get("memory_percent", 0), 1),
                "dl": round(m.get("disk_read_mbs", 0), 1),
                "de": round(m.get("disk_write_mbs", 0), 1),
                "red": round(m.get("network_down_mbps", 0), 1),
                "estado": "Online" if running else "Offline"
            }
    except Exception as e:
        # Si Fortinet bloquea o hay timeout, usamos el lector_api 
        print(f"Conexión directa fallida: {e}. Usando respaldo...")
        datos_finales = obtener_metricas_reales(nombre_limpio)

    if datos_finales:
        # alertas automaticas
        if datos_finales.get("estado") == "Offline":
            registrar_log(nombre_limpio, "CRITICAL", {"evento": "DOWNTIME DETECTADO"})
        elif datos_finales.get("cpu", 0) > 90:
            registrar_log(nombre_limpio, "WARNING", {"evento": "CPU SATURADO", "valor": datos_finales["cpu"]})

        #persistencia
        guardar_metrica_tiempo_real(nombre_limpio, datos_finales["cpu"], datos_finales["ram"])
        
        # Indicadores gerencia(Uptime/Incidencias)
        indicadores = obtener_indicadores_gerencia(nombre_limpio)
        datos_finales.update(indicadores)
        
        return datos_finales

    raise HTTPException(status_code=404, detail="Servicio no hallado")

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