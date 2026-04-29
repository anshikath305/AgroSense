# AgroSense Model Integration

## Backend routes

- `POST /crop/predict` loads `backend/crop/model_assets/RandomForest.pkl` and accepts `N`, `P`, `K`, `temperature`, `humidity`, `ph`, and `rainfall`.
- `POST /disease/analyze` accepts multipart `image`, optional `query`, and optional `lang`, then wraps `backend/disease/model/predict.py`. If `GEMINI_API_KEY` is not set, it still returns the disease model result with an advisory setup error.
- `POST /fertilizer/predict` loads the XGBoost classifier, quantity regressor, and encoders in `backend/fertilizer/model_assets`.
- `POST /advisory/ask` uses Gemini through `GEMINI_API_KEY`. If the key is missing, the endpoint returns a clear `503` error instead of fake advice.

## Frontend API proxies

The Next.js app calls local route handlers under `frontend/src/app/api/*`. These handlers proxy to FastAPI through `NEXT_PUBLIC_API_URL`, `AGROSENSE_BACKEND_URL`, or `NEXT_PUBLIC_BACKEND_URL`, defaulting to `http://127.0.0.1:8001`.

If the FastAPI server is not running, frontend routes return errors to the UI. They do not generate mock model outputs.

## IoT scope

IoT and sensor integrations are intentionally excluded from MVP v1. The code, navigation, and copy avoid exposing IoT as an active feature.
