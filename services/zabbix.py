import requests 


SERVICIOS_EMPRESA = [
    {"nombre": "JAC Venezuela", "ip": "10.0.0.50", "url": "https://jacvenezuela.com/"},
    {"nombre": "Bel Motos", "ip": "10.0.0.51", "url": "https://belmotos.com/"},
    {"nombre": "IntraBel", "ip": "10.0.0.52", "url": "https://intrabel.com.ve/"},
]


def obtener_metricas_reales(nombre_servicio):
    """
    Esta función sustituye a 'generarGraficoXservicio'.
    En lugar de crear una imagen, pide los números a la API.
    """
    url_api = f"http://127.0.0.1:8000/metricas/{nombre_servicio}"
    
    try:
     
        respuesta = requests.get(url_api, timeout=2) 
        
        if respuesta.status_code == 200:
        
            return respuesta.json()
        else:
            return {"error": "Servidor no responde"}
            
    except Exception as e:
      
        return {"error": "API desconectada"}


LOGS_SIMULADOS = {
    "10.0.0.50": [10, 15, 11], 
    "10.0.0.51": [9, 12],
    "10.0.0.52": [8],
}