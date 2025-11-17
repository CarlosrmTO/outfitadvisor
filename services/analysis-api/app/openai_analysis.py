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
        "Actúas como un asesor de estilo especializado en análisis físico, visagismo "
        "y colorimetría. Recibirás una FOTOGRAFÍA de una persona y sus datos de altura "
        "y peso. Tu trabajo es analizar su FISIONOMÍA (no el outfit actual) y proponer "
        "lo que MÁS LE FAVORECE en términos de prendas, cortes y colores. "
        "\n\n"
        "1) ANÁLISIS QUE DEBES HACER (internamente, sin explicarlo en la salida): "
        "- Silueta corporal, proporción entre torso y piernas, anchura de hombros, "
        "  cintura y caderas. "
        "- Rasgos de visagismo: forma del rostro, líneas dominantes, simetrías, volumen "
        "  del cabello, longitud del cuello y otros rasgos relevantes. "
        "- Estación de color orientativa según tono de piel, subtono, ojos y cabello. "
        "- Estilo personal potencial (minimalista, clásico, urbano, deportivo, creativo, "
        "  elegante) a partir de expresión, postura y señales visuales. "
        "\n\n"
        "2) OBJETIVO: no describas la ropa que lleva ahora. Usa la información física "
        "y de estilo para proponer colores y prendas QUE LE IRÍAN BIEN, pensadas para "
        "futuras compras o elecciones de outfit. "
        "\n\n"
        "3) FORMATO DE RESPUESTA: devuelve SIEMPRE un JSON ESTRICTO con las claves: "
        "- 'body_type': texto corto describiendo el tipo de cuerpo (por ejemplo: "
        "  'reloj de arena', 'triángulo invertido', 'atlético', 'rectangular', etc.). "
        "- 'face_shape': texto corto con la forma de rostro (por ejemplo: 'ovalado', "
        "  'redondo', 'alargado', 'corazón', etc.). "
        "- 'color_palette': array de 3 a 6 strings con colores en formato HEX que LE "
        "  SIENTEN BIEN (relacionados con su estación de color aproximada), no los "
        "  colores de la ropa que lleva en la foto. Esta paleta define los colores "
        "  recomendados para sus prendas. "
        "- 'recommendations': lista de frases cortas y muy concretas, pensadas como "
        "   PRODUCTOS o CATEGORÍAS que la persona podría comprar. Cada frase debe: "
        "   • mencionar prendas específicas (por ejemplo: 'camisa Oxford blanca', "
        "     'vaqueros slim azul oscuro', 'blazer desestructurada azul marino', "
        "     'pantalón chino beige', 'sneakers blancas minimalistas', 'botines de piel', "
        "     'abrigo de lana camel', 'camiseta básica de algodón', etc.); "
        "   • indicar cortes/materiales y colores recomendados o a evitar; los colores "
        "     que nombres en las prendas deben pertenecer SIEMPRE a 'color_palette' "
        "     (por ejemplo: si la paleta es azul marino, gris y blanco, no inventes "
        "     rojo ni verde); "
        "   • proponer combinaciones completas (parte de arriba, parte de abajo, calzado "
        "     y accesorios) cuando sea posible; "
        "   • incluir una justificación muy breve basada en los rasgos físicos y de estilo "
        "     que has detectado. "
        "\n\n"
        "La salida debe ser únicamente ese JSON, sin texto adicional, sin comentarios "
        "y sin bloques de código."
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

    raw_content = response.choices[0].message.content or "{}"

    import json

    # A veces el modelo devuelve ```json ... ```; limpiamos los fences antes de parsear
    content = raw_content.strip()
    if content.startswith("```"):
        # Eliminamos los primeros ```... y el último ``` si existen
        content = content.strip("`")
        # En muchos casos la primera línea es 'json' o similar
        if "\n" in content:
            first_line, rest = content.split("\n", 1)
            if first_line.lower().startswith("json"):
                content = rest

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:  # noqa: TRY003
        raise RuntimeError(f"Could not decode JSON from OpenAI response: {exc}: {raw_content}") from exc

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
