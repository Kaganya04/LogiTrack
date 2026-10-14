import logging

import httpx

from app import config
from app.locations import get_location

logger = logging.getLogger("logitrack.routing")

ASSUMPTIONS = [
    "Catalogue stops use approximate demo coordinates and geocoded stops use "
    "approximate OpenStreetMap matches. Neither is a verified customer address.",
    "Road-based travel estimates for one light van (auto profile).",
    "No live traffic, waiting time or service time.",
]


class RoutingError(Exception):
    """The routing engine failed or returned an unusable result."""


def build_vroom_request(depot, resolved, return_to_depot):
    """Build the VROOM payload and a map from VROOM job id to delivery id.

    VROOM expects coordinates as [longitude, latitude].
    """
    depot_point = [depot["lng"], depot["lat"]]
    vehicle = {
        "id": 1,
        "description": "Delivery van",
        "profile": "auto",
        "start": depot_point,
    }
    if return_to_depot:
        vehicle["end"] = depot_point

    jobs = []
    job_to_delivery = {}
    for job_id, (delivery_id, location) in enumerate(resolved, start=1):
        jobs.append({"id": job_id, "location": [location["lng"], location["lat"]]})
        job_to_delivery[job_id] = delivery_id
    return {"vehicles": [vehicle], "jobs": jobs}, job_to_delivery


def parse_vroom_response(data, job_to_delivery):
    """Check the VROOM answer and translate it into app data."""
    if data.get("code") != 0:
        raise RoutingError("The routing engine could not plan this route.")
    if data.get("unassigned"):
        raise RoutingError("Some deliveries could not be assigned to the route.")
    routes = data.get("routes", [])
    if len(routes) != 1:
        raise RoutingError("The routing engine returned an unexpected result.")

    route = routes[0]
    job_ids = [s["id"] for s in route["steps"] if s["type"] == "job"]
    if sorted(job_ids) != sorted(job_to_delivery):
        raise RoutingError("The route did not include every delivery exactly once.")

    return {
        "ordered_delivery_ids": [job_to_delivery[job_id] for job_id in job_ids],
        "total_distance_km": route["distance"] / 1000,
        "driving_time_minutes": route["duration"] / 60,
    }


def optimize_deliveries(depot_id, deliveries, return_to_depot):
    """Order the deliveries for one van using VROOM with Valhalla road costs.

    deliveries is a list of dicts with "id" and either "location_id" or "lat" and
    "lng" (already checked against the Hyderabad box by the request schema).
    Raises ValueError for unknown ids and RoutingError for engine problems.
    """
    depot = get_location(depot_id)
    if depot is None:
        raise ValueError(f"Unknown depot: {depot_id}")

    resolved = []
    for delivery in deliveries:
        if delivery.get("location_id") is None:
            resolved.append((delivery["id"], {"lat": delivery["lat"], "lng": delivery["lng"]}))
            continue
        location = get_location(delivery["location_id"])
        if location is None:
            raise ValueError(f"Unknown location: {delivery['location_id']}")
        resolved.append((delivery["id"], location))

    payload, job_to_delivery = build_vroom_request(depot, resolved, return_to_depot)

    try:
        response = httpx.post(
            config.VROOM_URL, json=payload, timeout=config.REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError) as error:
        logger.error("VROOM request failed: %s", type(error).__name__)
        raise RoutingError("The routing engine is temporarily unavailable.") from error

    try:
        result = parse_vroom_response(data, job_to_delivery)
    except (KeyError, TypeError) as error:
        logger.error("VROOM response had an unexpected shape")
        raise RoutingError("The routing engine returned an unexpected result.") from error

    result["depot_id"] = depot_id
    result["return_to_depot"] = return_to_depot
    result["assumptions"] = ASSUMPTIONS
    return result
