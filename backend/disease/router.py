from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.datastructures import UploadFile

from .service import MODEL_NOT_TRAINED_MESSAGE, ModelNotTrainedError, analyze_leaf_image

router = APIRouter()


@router.post("/analyze")
async def analyze(request: Request) -> dict:
    try:
        form = await request.form()
        image = form.get("image")
        if not isinstance(image, UploadFile):
            raise ValueError("Multipart field 'image' is required.")
        query = str(form.get("query") or "What treatment should I use?")
        lang = str(form.get("lang") or "en")
        return await analyze_leaf_image(image=image, query=query, lang=lang)
    except ModelNotTrainedError:
        return JSONResponse(status_code=503, content={"status": "error", "error": MODEL_NOT_TRAINED_MESSAGE})
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"status": "error", "error": str(exc)})
    except Exception as exc:
        message = str(exc)
        if message == MODEL_NOT_TRAINED_MESSAGE:
            return JSONResponse(status_code=503, content={"status": "error", "error": MODEL_NOT_TRAINED_MESSAGE})
        if "GEMINI_API_KEY" in message or "Advisory model" in message:
            raise HTTPException(status_code=503, detail=message) from exc
        raise HTTPException(status_code=500, detail=message) from exc
