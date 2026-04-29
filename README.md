# AgroSense

AgroSense is an AI powered smart farming MVP with crop recommendation, plant disease detection, fertilizer prediction, and an AI farming advisory assistant.

## Structure

```text
frontend/   Next.js App Router web platform
backend/    FastAPI model-serving API
assets/     Stitch visual references and shared assets
docs/       Design and integration notes
public/     Shared public assets placeholder
```

## Run the backend

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8001
```

Set `GEMINI_API_KEY` in `backend/.env` to enable live AI advisory. Without it, the advisory endpoint returns a clear setup error instead of canned advice.

## Run the frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

## Core routes

- `/` home page
- `/crop-ai` crop recommendation
- `/disease-ai` disease detection
- `/fertilizer-ai` fertilizer prediction
- `/assistant` AI advisory assistant
- `/about` about page
- `/contact` contact page
- `/login` and `/signup` auth-ready placeholders

## Deployment

- Deploy `frontend/` to Vercel.
- Deploy `backend/` to Render, Railway, AWS, or another Python host.
- Point `NEXT_PUBLIC_API_URL` to the deployed FastAPI base URL.
