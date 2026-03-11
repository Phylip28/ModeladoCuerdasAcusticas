"""FastAPI application — Modelado de Cuerdas Acústicas.

Run with:
    uvicorn backend.main:app --reload --port 8000
"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.routers import data, train, predict, report

# App

app = FastAPI(
    title="Modelado de Cuerdas Acústicas",
    description=(
        "API REST para cargar datos de guitarra, entrenar modelos de regresión "
        "(Polinomial, MLP, SVR) y generar reportes PDF comparativos."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — permite peticiones desde el dev server de Vite (puerto 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ───────────────────────────────────────────────────────────────

app.include_router(data.router, prefix="/api")
app.include_router(train.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(report.router, prefix="/api")


# ─── Healthcheck ───────────────────────────────────────────────────────────


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "app": "Modelado de Cuerdas Acústicas"}
