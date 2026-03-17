from fastapi import FastAPI
import random 

app = FastAPI()

@app.get("/")
def inicio():
    return {"mensaje": "API de InfraMonitor Bel Activa"}

@app.get("/metricas/{servicio}")
def obtener_metricas(servicio: str):
   
    return {
        "servicio": servicio,
        "cpu": random.randint(10, 95),  
        "ram": random.randint(20, 80),
        "red": random.randint(5, 100),
        "estado": "Online"
    }
