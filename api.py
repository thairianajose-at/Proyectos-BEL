from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # IMPORTANTE
from urllib.parse import unquote
import uvicorn # Para lanzarla correctamente
from controladores.crud import registrar_log, obtener_logs_para_grafica
from services.zabbix import obtener_metricas_reales, SERVICIOS_EMPRESA

app = FastAPI()

# --- CONFIGURACIÓN DE CORS (Soluciona el rechazo en Web) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite que cualquier IP (tu dashboard) se conecte
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, etc.
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
    res = registrar_log(nivel, datos)
    return {"message": "Log guardado", "id": res.id}

@app.get("/metricas/{nombre_app}")
async def enviar_metricas_especificas(nombre_app: str):
    nombre_limpio = unquote(nombre_app)
    datos = obtener_metricas_reales(nombre_limpio)
    
    if not datos or "error" in datos:
        raise HTTPException(
            status_code=404, 
            detail=f"El servicio '{nombre_limpio}' no fue encontrado en Zabbix"
        )
    return datos

@app.get("/metricas-historicas")
def enviar_metricas_historicas():
    logs = obtener_logs_para_grafica()
    return logs

# --- LANZADOR DE LA API ---
if __name__ == "__main__":
    # host="0.0.0.0" permite que la API sea vista en toda la red de la empresa
    uvicorn.run(app, host="0.0.0.0", port=8000)