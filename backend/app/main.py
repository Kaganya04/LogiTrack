import logging

from fastapi import FastAPI, HTTPException

from app.llm import LLMError, extract_deliveries
from app.locations import load_locations
from app.preprocessing import clean_text
from app.routing import RoutingError, optimize_deliveries
from app.schemas import (
    OptimizeRequest,
    OptimizeResponse,
    ParseRequest,
    ParseResponse,
)

logger = logging.getLogger("logitrack.api")

app = FastAPI(title="LogiTrack")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/parse", response_model=ParseResponse)
def parse(request: ParseRequest):
    """Extract delivery addresses from free text and resolve them to the catalogue."""
    deliveries = []
    for delivery in request.deliveries:
        text = clean_text(delivery.text)
        if not text:
            raise HTTPException(status_code=422, detail="Delivery text must not be blank.")
        deliveries.append({"id": delivery.id, "text": text})
    try:
        return extract_deliveries(deliveries, clean_text(request.instructions))
    except LLMError as error:
        raise HTTPException(status_code=503, detail=str(error))


@app.post("/api/optimize", response_model=OptimizeResponse)
def optimize(request: OptimizeRequest):
    """Order the confirmed deliveries for one van."""
    try:
        return optimize_deliveries(
            request.depot_id,
            [delivery.model_dump() for delivery in request.deliveries],
            request.return_to_depot,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))
    except RoutingError as error:
        raise HTTPException(status_code=503, detail=str(error))


@app.get("/api/locations")
def locations():
    """List the supported demo locations for the form."""
    return [
        {"id": item["id"], "name": item["name"]}
        for item in load_locations().values()
    ]
