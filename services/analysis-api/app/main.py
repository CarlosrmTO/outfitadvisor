from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .models import AnalysisResult
from .openai_analysis import analyze_with_openai

app = FastAPI(title="OutfitAdvisor Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(
    height: float = Form(...),
    weight: float = Form(...),
    photo: UploadFile = File(None),
):
    if photo is None:
        raise HTTPException(status_code=400, detail="Image (photo) is required")

    if not photo.content_type or not photo.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    try:
        image_bytes = await photo.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded image is empty")

        result = analyze_with_openai(
            image_bytes=image_bytes,
            height=height,
            weight=weight,
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail=f"Error while analyzing image with OpenAI: {exc}",
        ) from exc

    return {"status": "success", "analysis": result.model_dump()}
