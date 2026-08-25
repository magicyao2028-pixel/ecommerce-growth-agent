from __future__ import annotations

from typing import Any

from .service_contract import analyze_request


def create_fastapi_app() -> Any:
    """Create an optional FastAPI adapter without making FastAPI a runtime dependency."""
    try:
        from fastapi import FastAPI, HTTPException
    except ImportError as exc:
        raise RuntimeError(
            "FastAPI adapter is optional; install the free service extra to run the HTTP boundary."
        ) from exc

    app = FastAPI(title="E-commerce Growth Agent", version="0.7.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "ecommerce-growth-agent"}

    @app.post("/v1/analyze")
    def analyze(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return analyze_request(payload)
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return app
