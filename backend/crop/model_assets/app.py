from fastapi import FastAPI
import joblib
import numpy as np
import requests

app = FastAPI()

model = joblib.load("RandomForest.pkl")

API_KEY = "9e62cff42dd6651172e71984741a32ba"


@app.get("/")
def home():
    return {"message": "AgroSense Weather AI Running"}


@app.post("/predict")
def predict(data: dict):

    values = np.array([[
        data["N"],
        data["P"],
        data["K"],
        data["temperature"],
        data["humidity"],
        data["ph"],
        data["rainfall"]
    ]])

    probs = model.predict_proba(values)[0]
    labels = model.classes_

    top3 = sorted(zip(labels, probs), key=lambda x: x[1], reverse=True)[:3]

    return {
        "recommendations": [
            {"crop": crop, "score": round(score * 100, 2)}
            for crop, score in top3 if score > 0
        ]
    }


@app.post("/predict-by-location")
def predict_by_location(data: dict):

    city = data["city"]

    # ---------- Input Validation ----------
    if data["N"] < 0 or data["P"] < 0 or data["K"] < 0:
        return {"error": "NPK values cannot be negative"}

    if data["ph"] < 0 or data["ph"] > 14:
        return {"error": "pH must be between 0 and 14"}

    # ---------- Geocoding ----------
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo = requests.get(geo_url).json()

    if "results" not in geo:
        return {"error": "City not found"}

    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]

    # ---------- Weather ----------
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,rain"

    weather = requests.get(weather_url).json()
    current = weather["current"]

    temp = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    rainfall = current["rain"]

    # ---------- Prediction ----------
    values = np.array([[
        data["N"],
        data["P"],
        data["K"],
        temp,
        humidity,
        data["ph"],
        rainfall
    ]])

    probs = model.predict_proba(values)[0]
    labels = model.classes_

    top = sorted(zip(labels, probs), key=lambda x: x[1], reverse=True)

    recommendations = []

    for crop, score in top[:5]:

        if score <= 0:
            continue

        percent = round(score * 100, 2)

        if percent >= 70:
            confidence = "High"
        elif percent >= 40:
            confidence = "Medium"
        else:
            confidence = "Low"

        recommendations.append({
            "crop": crop,
            "score": percent,
            "confidence": confidence
        })

    # ---------- Smart Advice ----------
    advice = []

    if temp > 35:
        advice.append("High temperature detected. Use irrigation regularly.")

    if humidity < 30:
        advice.append("Low humidity. Soil may dry faster.")

    if rainfall > 5:
        advice.append("Rain expected. Avoid overwatering.")

    if data["ph"] < 5.5:
        advice.append("Soil acidic. Consider lime treatment.")

    if data["ph"] > 8:
        advice.append("Soil alkaline. Add organic compost.")

    return {
        "city": city,
        "weather": {
            "temperature": temp,
            "humidity": humidity,
            "rainfall": rainfall
        },
        "recommendations": recommendations[:3],
        "advice": advice
    }