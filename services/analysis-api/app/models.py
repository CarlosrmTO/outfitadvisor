from pydantic import BaseModel
from typing import List


class AnalysisResult(BaseModel):
    body_type: str
    face_shape: str
    color_palette: List[str]
    recommendations: List[str]
