from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="OutfitAdvisor Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisResult(BaseModel):
    body_type: str
    face_shape: str
    color_palette: List[str]
    recommendations: List[str]


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

    dummy_result = AnalysisResult(
        body_type="hourglass",
        face_shape="oval",
        color_palette=["#F5A9B8", "#A9D0F5", "#F2F5A9"],
        recommendations=[
            "Vestidos entallados que marquen cintura",
            "Cuellos en V para estilizar la parte superior",
            "Colores suaves y cálidos cerca del rostro",
        ],
    )

    return {"status": "success", "analysis": dummy_result.model_dump()}
