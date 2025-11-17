from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List


class AnalysisInput(BaseModel):
    body_type: str
    face_shape: str
    color_palette: List[str]
    style_hint: str | None = None
    categories: List[str]


class ProductItem(BaseModel):
    name: str
    store: str
    category: str
    url: str


class RecommendationResponse(BaseModel):
    items: List[ProductItem]


app = FastAPI(title="OutfitAdvisor Recommendation Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # No necesitamos credenciales (cookies/autenticación de navegador) en este
    # servicio público de recomendaciones, así que desactivamos credentials
    # para simplificar el manejo de CORS y evitar problemas en preflight.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


@app.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(payload: AnalysisInput) -> RecommendationResponse:
    # Versión inicial: catálogo mock muy simple
    mock_items = [
        ProductItem(
            name="Camisa Oxford blanca slim fit",
            store="Zara",
            category="camisa",
            url="https://example.com/zara/camisa-oxford-blanca",
        ),
        ProductItem(
            name="Vaqueros slim azul oscuro",
            store="Uniqlo",
            category="vaqueros",
            url="https://example.com/uniqlo/vaqueros-slim-azul-oscuro",
        ),
    ]

    return RecommendationResponse(items=mock_items)
