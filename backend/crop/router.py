from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .service import CropFeatures, predict_crop

router = APIRouter()


class CropRequest(BaseModel):
    nitrogen: float = Field(..., ge=0, alias="N")
    phosphorus: float = Field(..., ge=0, alias="P")
    potassium: float = Field(..., ge=0, alias="K")
    temperature: float
    humidity: float = Field(..., ge=0, le=100)
    ph: float = Field(..., ge=0, le=14)
    rainfall: float = Field(..., ge=0)

    class Config:
        populate_by_name = True


@router.post("/predict")
def predict(payload: CropRequest) -> dict:
    try:
        features = CropFeatures(
            nitrogen=payload.nitrogen,
            phosphorus=payload.phosphorus,
            potassium=payload.potassium,
            temperature=payload.temperature,
            humidity=payload.humidity,
            ph=payload.ph,
            rainfall=payload.rainfall,
        )
        return predict_crop(features)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
