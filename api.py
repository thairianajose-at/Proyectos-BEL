from fastapi import FastAPI, HTTPException
from urllib.parse import unquote
from controladores.crud import registrar_log, obtener_logs_para_grafica
from services.zabbix import obtener_metricas_reales, SERVICIOS_EMPRESA

app = FastAPI()

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