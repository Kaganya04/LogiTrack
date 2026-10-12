import logging

from fastapi import FastAPI, HTTPException

from app.routing import RoutingError, optimize_deliveries
from app.schemas import OptimizeRequest, OptimizeResponse

logger = logging.getLogger("logitrack.api")

app = FastAPI(title="LogiTrack")


@app.get("/api/health")
def health():
    return {"status": "ok"}


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
