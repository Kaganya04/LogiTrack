import logging
import time
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app import config
from app.llm import LLMError, extract_deliveries
from app.locations import load_locations
from app.logging_config import request_id_var, setup_logging
from app.preprocessing import clean_text
from app.routing import RoutingError, optimize_deliveries
from app.schemas import (
    OptimizeRequest,
    OptimizeResponse,
    ParseRequest,
    ParseResponse,
)

setup_logging()
logger = logging.getLogger("logitrack.api")
if config.LLM_STUB:
    logger.warning("LLM stub mode is ON")

app = FastAPI(title="LogiTrack")


@app.middleware("http")
async def log_requests(request, call_next):
    """Give each request an id and log its endpoint, status and duration."""
    request_id = uuid.uuid4().hex[:8]
    token = request_id_var.set(request_id)
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled error on %s", request.url.path)
        response = JSONResponse(status_code=500, content={"detail": "Something went wrong."})
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    outcome = "ok" if response.status_code < 400 else "error"
    logger.info(
        "%s %s -> %s in %d ms (%s)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
        outcome,
    )
    response.headers["X-Request-ID"] = request_id
    request_id_var.reset(token)
    return response


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/locations")
def locations():
    """List the supported demo locations for the form."""
    return [
        {"id": item["id"], "name": item["name"]}
        for item in load_locations().values()
    ]


@app.post("/api/parse", response_model=ParseResponse)
def parse(request: ParseRequest):
    """Extract delivery addresses from free text and resolve them (catalogue, then geocoder)."""
    logger.info("parse requested: %d deliveries", len(request.deliveries))
    deliveries = []
    for delivery in request.deliveries:
        text = clean_text(delivery.text)
        if not text:
            raise HTTPException(status_code=422, detail="Delivery text must not be blank.")
        deliveries.append({"id": delivery.id, "text": text})
    try:
        return extract_deliveries(deliveries, clean_text(request.instructions))
    except LLMError as error:
        logger.warning("parse failed: category=llm")
        raise HTTPException(status_code=503, detail=str(error))


@app.post("/api/optimize", response_model=OptimizeResponse)
def optimize(request: OptimizeRequest):
    """Order the confirmed deliveries for one van."""
    logger.info(
        "optimize requested: %d deliveries, round_trip=%s",
        len(request.deliveries),
        request.return_to_depot,
    )
    try:
        return optimize_deliveries(
            request.depot_id,
            [delivery.model_dump() for delivery in request.deliveries],
            request.return_to_depot,
        )
    except ValueError as error:
        logger.warning("optimize failed: category=validation")
        raise HTTPException(status_code=422, detail=str(error))
    except RoutingError as error:
        logger.warning("optimize failed: category=routing")
        raise HTTPException(status_code=503, detail=str(error))
