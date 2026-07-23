from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI(
    title="API de Cuotas y Predicciones de Fútbol",
    description="Obtiene cuotas en tiempo real y calcula la predicción del partido.",
    version="1.0.0"
)

# Puedes colocar tu API Key de TheOddsAPI aquí o configurarla en las variables de entorno de Render
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "TU_API_KEY_AQUI")
SPORT = "soccer_epl"  # Premier League de Inglaterra

@app.get("/")
def home():
    return {"message": "API de Apuestas y Predicciones activa. Ve a /docs para probarla."}

@app.get("/predict")
def get_predictions():
    if ODDS_API_KEY == 4da0cf222f158b264f253e07d0f337c6:
        raise HTTPException(status_code=400, detail="Falta configurar la ODDS_API_KEY")

    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error al consultar TheOddsAPI")

    data = response.json()
    predictions = []

    for match in data:
        home_team = match.get("home_team")
        away_team = match.get("away_team")
        
        # Buscar el primer bookmaker disponible (ej. Unibet, Bet365, etc.)
        bookmakers = match.get("bookmakers", [])
        if not bookmakers:
            continue
        
        outcomes = bookmakers[0]["markets"][0]["outcomes"]
        
        odds = {}
        for outcome in outcomes:
            odds[outcome["name"]] = outcome["price"]

        home_price = odds.get(home_team)
        away_price = odds.get(away_team)
        draw_price = odds.get("Draw")

        if home_price and away_price and draw_price:
            # 1. Probabilidades implícitas brutas
            raw_home = 1 / home_price
            raw_draw = 1 / draw_price
            raw_away = 1 / away_price
            
            # Margen total de la casa de apuestas
            margin = raw_home + raw_draw + raw_away

            # 2. Probabilidades reales ajustadas (sin margen)
            prob_home = round((raw_home / margin) * 100, 2)
            prob_draw = round((raw_draw / margin) * 100, 2)
            prob_away = round((raw_away / margin) * 100, 2)

            # 3. Determinación de la predicción
            probs = {
                f"Gana {home_team}": prob_home,
                "Empate": prob_draw,
                f"Gana {away_team}": prob_away
            }
            
            # Resultado con mayor probabilidad
            predicted_outcome = max(probs, key=probs.get)
            confidence = probs[predicted_outcome]

            predictions.append({
                "partido": f"{home_team} vs {away_team}",
                "prediccion": predicted_outcome,
                "confianza": f"{confidence}%",
                "probabilidades": {
                    home_team: f"{prob_home}%",
                    "Empate": f"{prob_draw}%",
                    away_team: f"{prob_away}%"
                },
                "cuotas_originales": {
                    home_team: home_price,
                    "Empate": draw_price,
                    away_team: away_price
                }
            })

    return {"total_partidos": len(predictions), "predicciones": predictions}
