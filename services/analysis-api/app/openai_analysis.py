import base64
import io
import os
from typing import List

from dotenv import load_dotenv
from openai import OpenAI

from .models import AnalysisResult


load_dotenv()


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key)


def _encode_image_to_base64(file_bytes: bytes) -> str:
    return base64.b64encode(file_bytes).decode("utf-8")


def analyze_with_openai(
    *,
    image_bytes: bytes,
    height: float,
    weight: float,
) -> AnalysisResult:
    """Call OpenAI to analyze body type, face shape and color palette.

    This is a first version that uses a single multimodal call and expects
    a structured JSON answer that we parse into AnalysisResult.
    """

    client = _get_client()
    b64_image = _encode_image_to_base64(image_bytes)

    system_prompt = (
        "Eres un asesor de imagen experto en tipología corporal, visagismo y "
        "colorimetría. A partir de una fotografía de la persona y sus datos "
        "(altura y peso), debes devolver un análisis estructurado en JSON "
        "con: 'body_type' (texto corto), 'face_shape' (texto corto), "
        "'color_palette' (array de 3 a 6 colores en hex) y "
        "'recommendations' (lista de frases cortas con recomendaciones de prendas)."
    )

    user_prompt = (
        "Datos de la persona:"\
        f" Altura: {height} cm. Peso: {weight} kg. "
        "Responde solo con JSON válido, sin texto adicional."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_image}",
                        },
                    },
                ],
            },
        ],
    )

    content = response.choices[0].message.content or "{}"

    import json

    data = json.loads(content)

    body_type = str(data.get("body_type", "desconocido"))
    face_shape = str(data.get("face_shape", "desconocido"))
    color_palette_raw = data.get("color_palette") or []
    recommendations_raw = data.get("recommendations") or []

    color_palette: List[str] = [str(c) for c in color_palette_raw][:6]
    recommendations: List[str] = [str(r) for r in recommendations_raw][:10]

    if not color_palette:
        color_palette = ["#F5A9B8", "#A9D0F5", "#F2F5A9"]

    if not recommendations:
        recommendations = [
            "Prendas que marquen ligeramente la cintura",
            "Evitar cortes que rompan en zonas muy anchas del cuerpo",
        ]

    return AnalysisResult(
        body_type=body_type,
        face_shape=face_shape,
        color_palette=color_palette,
        recommendations=recommendations,
    )
