from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .service import FertilizerFeatures, get_supported_values, predict_fertilizer

router = APIRouter()


class FertilizerRequest(BaseModel):
    temperature: float = Field(..., alias="Temparature")
    humidity: float = Field(..., ge=0, le=100, alias="Humidity")
    moisture: float = Field(..., ge=0, le=100)
    soil_type: str
    crop_type: str
    nitrogen: float = Field(..., ge=0)
    potassium: float = Field(..., ge=0)
    phosphorous: float = Field(..., ge=0)

    class Config:
        populate_by_name = True


@router.get("/options")
def options() -> dict:
    return get_supported_values()


@router.post("/predict")
def predict(payload: FertilizerRequest) -> dict:
    try:
        features = FertilizerFeatures(
            temperature=payload.temperature,
            humidity=payload.humidity,
            moisture=payload.moisture,
            soil_type=payload.soil_type,
            crop_type=payload.crop_type,
            nitrogen=payload.nitrogen,
            potassium=payload.potassium,
            phosphorous=payload.phosphorous,
        )
        return predict_fertilizer(features)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
