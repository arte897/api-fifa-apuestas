from fastapi import FastAPI
import requests

app = FastAPI()

ODDS_API_KEY = "TU_API_KEY_AQUI"

@app.get("/")
def inicio():
    return {"mensaje": "¡Mi API de Estadísticas está activa!"}

@app.get("/cuotas")
def obtener_cuotas():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=h2h"
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        return respuesta.json()
    return {"error": "No se pudieron obtener las cuotas", "detalle": respuesta.text}

