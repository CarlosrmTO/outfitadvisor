"use client";

import { FormEvent, useState } from "react";

type Analysis = {
  body_type: string;
  face_shape: string;
  color_palette: string[];
  recommendations: string[];
};

export default function Home() {
  const [height, setHeight] = useState<string>("");
  const [weight, setWeight] = useState<string>("");
  const [photo, setPhoto] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setAnalysis(null);

    if (!photo) {
      setError("Por favor, sube una foto.");
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append("height", height);
      formData.append("weight", weight);
      formData.append("photo", photo);

      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        const message = data?.detail || "Ha ocurrido un error al analizar la imagen.";
        throw new Error(message);
      }

      const data = await response.json();
      setAnalysis(data.analysis as Analysis);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Error desconocido";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-12 col-lg-10">
          <div className="card shadow-sm">
            <div className="card-body p-4 p-md-5">
              <h1 className="h3 mb-3">OutfitAdvisor</h1>
              <p className="text-muted mb-4">
                Sube tu foto y dinos tu altura y peso. Analizaremos tu tipo de cuerpo, rasgos faciales
                y colorimetría para recomendarte las prendas que mejor encajan contigo.
              </p>

              <form onSubmit={handleSubmit} className="row g-3">
                <div className="col-12 col-md-6">
                  <label htmlFor="height" className="form-label">
                    Altura (cm)
                  </label>
                  <input
                    id="height"
                    type="number"
                    min={100}
                    max={230}
                    className="form-control"
                    value={height}
                    onChange={(e) => setHeight(e.target.value)}
                    required
                  />
                </div>

                <div className="col-12 col-md-6">
                  <label htmlFor="weight" className="form-label">
                    Peso (kg)
                  </label>
                  <input
                    id="weight"
                    type="number"
                    min={30}
                    max={250}
                    className="form-control"
                    value={weight}
                    onChange={(e) => setWeight(e.target.value)}
                    required
                  />
                </div>

                <div className="col-12">
                  <label htmlFor="photo" className="form-label">
                    Foto (cuerpo entero o rostro)
                  </label>
                  <input
                    id="photo"
                    type="file"
                    accept="image/*"
                    className="form-control"
                    onChange={(e) => {
                      const file = e.target.files?.[0] ?? null;
                      setPhoto(file);
                    }}
                    required
                  />
                  <div className="form-text">
                    En esta primera versión solo usamos una foto. Más adelante podremos separar cuerpo y rostro.
                  </div>
                </div>

                {error && (
                  <div className="col-12">
                    <div className="alert alert-danger" role="alert">
                      {error}
                    </div>
                  </div>
                )}

                <div className="col-12 d-flex justify-content-end">
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? "Analizando..." : "Analizar y recomendar"}
                  </button>
                </div>
              </form>

              {analysis && (
                <div className="mt-5">
                  <h2 className="h5 mb-3">Tu análisis</h2>
                  <div className="row g-3">
                    <div className="col-12 col-md-4">
                      <div className="border rounded p-3 h-100">
                        <h3 className="h6 text-uppercase text-muted">Tipo de cuerpo</h3>
                        <p className="mb-0 fw-semibold">{analysis.body_type}</p>
                      </div>
                    </div>
                    <div className="col-12 col-md-4">
                      <div className="border rounded p-3 h-100">
                        <h3 className="h6 text-uppercase text-muted">Rostro</h3>
                        <p className="mb-0 fw-semibold">{analysis.face_shape}</p>
                      </div>
                    </div>
                    <div className="col-12 col-md-4">
                      <div className="border rounded p-3 h-100">
                        <h3 className="h6 text-uppercase text-muted mb-2">Colorimetría</h3>
                        <div className="d-flex flex-wrap gap-2">
                          {analysis.color_palette.map((color) => (
                            <span
                              key={color}
                              className="rounded-circle border"
                              style={{
                                display: "inline-block",
                                width: 24,
                                height: 24,
                                backgroundColor: color,
                              }}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4">
                    <h3 className="h6 text-uppercase text-muted mb-2">
                      Recomendaciones de prendas
                    </h3>
                    <ul className="list-group">
                      {analysis.recommendations.map((item, index) => (
                        <li key={index} className="list-group-item">
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
