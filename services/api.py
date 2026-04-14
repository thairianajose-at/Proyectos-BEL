from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from urllib.parse import unquote
import uvicorn 
import requests
from controladores.crud import registrar_log, guardar_metrica_tiempo_real, obtener_indicadores_gerencia
from database.config import SessionLocal

app = FastAPI()

# IP del Agente de Monitoreo de la Infraestructura
URL_INFRA_REAL = "http://172.17.16.18:8000/api/containers" 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

@app.get("/metricas/{nombre_app}")
async def enviar_metricas_especificas(nombre_app: str):
    nombre_limpio = unquote(nombre_app)
    
    try:
        # 1. Consumo de la Infraestructura Real
        res = requests.get(URL_INFRA_REAL, timeout=2.5)
        contenedores = res.json()
        
        # 2. Búsqueda del contenedor específico
        match = next((c for c in contenedores if c.get("name") == nombre_limpio), None)
        
        if not match:
            raise HTTPException(status_code=404, detail="Contenedor no hallado")

        # 3. Extracción de MÉTRICAS EXPANDIDAS
        m = match.get("health", {}).get("metrics", {})
        running = match.get("running", False)
        
        # Mapeamos los nombres del Agente Docker a nuestro estándar de Dashboard
        datos_finales = {
            "nombre": nombre_limpio,
            "cpu": round(m.get("cpu_percent", 0), 1),
            "ram": round(m.get("memory_percent", 0), 1),
            "dl": round(m.get("disk_read_mbs", 0), 1),  # Lectura de disco
            "de": round(m.get("disk_write_mbs", 0), 1), # Escritura de disco
            "red": round(m.get("network_down_mbps", 0), 1),
            "estado": "Online" if running else "Offline"
        }

        # 4. Lógica de Alertas Automáticas
        if not running:
            registrar_log(nombre_limpio, "CRITICAL", {"evento": "DOWNTIME DETECTADO"})
        elif datos_finales["cpu"] > 90:
            registrar_log(nombre_limpio, "WARNING", {"evento": "CPU SATURADO", "valor": datos_finales["cpu"]})

        # 5. Persistencia y Estadísticas de Gerencia
        # Guardamos CPU y RAM para las gráficas históricas
        guardar_metrica_tiempo_real(nombre_limpio, datos_finales["cpu"], datos_finales["ram"])
        
        # Agregamos Uptime e Incidencias calculadas desde la DB
        indicadores = obtener_indicadores_gerencia(nombre_limpio)
        datos_finales.update(indicadores)
        
        return datos_finales

    except Exception as e:
        print(f"Error en API: {e}")
        return {
            "nombre": nombre_limpio, "estado": "Desconectado",
            "cpu": 0, "ram": 0, "dl": 0, "de": 0, "red": 0,
            "uptime": "0%", "incidencias": 0
        }

if __name__ == "__main__":
    # Ejecución en el puerto 8000 para que lector_api lo encuentre
    uvicorn.run(app, host="0.0.0.0", port=8000)