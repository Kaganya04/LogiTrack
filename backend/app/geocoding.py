import logging
import math
import threading
import time
from collections import OrderedDict

import httpx

from app import config
from app.locations import normalize

logger = logging.getLogger("logitrack.geocoding")

_lock = threading.Lock()
_cache = OrderedDict()
_last_request = float("-inf")


class GeocodingError(Exception):
    """The geocoder is turned off, failed or returned an unusable answer."""


def inside_hyderabad(lat, lng):
    """Return True when the point lies inside the configured Hyderabad box."""
    box = config.HYDERABAD_BBOX
    return box["min_lat"] <= lat <= box["max_lat"] and box["min_lng"] <= lng <= box["max_lng"]


def reset():
    """Clear the cache and the rate limit clock."""
    global _last_request
    with _lock:
        _cache.clear()
        _last_request = float("-inf")


def _is_enabled():
    agent = config.NOMINATIM_USER_AGENT.strip()
    return config.GEOCODER_ENABLED and bool(agent) and not agent.startswith("replace_with")


def _request(text):
    """Send one search bounded to Hyderabad, at most one request per interval."""
    global _last_request
    box = config.HYDERABAD_BBOX
    params = {
        "q": text,
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "in",
        "viewbox": f"{box['min_lng']},{box['max_lat']},{box['max_lng']},{box['min_lat']}",
        "bounded": 1,
    }
    with _lock:
        wait = config.GEOCODER_MIN_INTERVAL_SECONDS - (time.monotonic() - _last_request)
        if wait > 0:
            time.sleep(wait)
        try:
            response = httpx.get(
                config.NOMINATIM_URL,
                params=params,
                headers={"User-Agent": config.NOMINATIM_USER_AGENT},
                timeout=config.GEOCODER_TIMEOUT_SECONDS,
            )
        finally:
            _last_request = time.monotonic()
    response.raise_for_status()
    return response.json()


def _parse(data):
    """Return the first match inside the box, None for no usable match."""
    if not isinstance(data, list):
        raise GeocodingError("The address lookup returned an unexpected result.")
    if not data:
        logger.info("geocode result: category=no_match")
        return None
    try:
        first = data[0]
        lat = float(first["lat"])
        lng = float(first["lon"])
        name = str(first.get("display_name") or "")
    except (AttributeError, KeyError, TypeError, ValueError):
        raise GeocodingError("The address lookup returned an unexpected result.") from None
    if not (math.isfinite(lat) and math.isfinite(lng)) or not inside_hyderabad(lat, lng):
        logger.info("geocode result: category=outside_box")
        return None
    logger.info("geocode result: category=match")
    return {"lat": lat, "lng": lng, "display_name": name}


def geocode(text):
    """Look up an address in Hyderabad with Nominatim.

    Returns {"lat", "lng", "display_name"} or None when nothing inside the box
    matches. Raises GeocodingError when the geocoder is off or fails. Address text
    is never logged; httpx errors carry the request URL, so they are not chained.
    """
    if not _is_enabled():
        logger.warning("geocode skipped: category=disabled")
        raise GeocodingError("The address lookup service is not available.")

    key = normalize(text)
    if not key:
        return None
    with _lock:
        if key in _cache:
            _cache.move_to_end(key)
            logger.info("geocode result: category=cache_hit")
            return _cache[key]

    try:
        data = _request(text)
    except httpx.TimeoutException:
        logger.warning("geocode failed: category=timeout")
        raise GeocodingError("The address lookup service is not available.") from None
    except (httpx.HTTPError, ValueError) as error:
        logger.warning("geocode failed: category=http_error (%s)", type(error).__name__)
        raise GeocodingError("The address lookup service is not available.") from None

    try:
        result = _parse(data)
    except GeocodingError:
        logger.warning("geocode failed: category=bad_response")
        raise

    with _lock:
        _cache[key] = result
        _cache.move_to_end(key)
        while len(_cache) > config.GEOCODER_CACHE_SIZE:
            _cache.popitem(last=False)
    return result
