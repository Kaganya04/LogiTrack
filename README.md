# LogiTrack

LogiTrack helps a logistics manager plan the delivery order for one light van. The manager types delivery addresses in plain language, reviews what the system understood, and gets an ordered route with estimated road distance and driving time.

## Overview
- **Input:** up to 8 delivery lines, a depot, optional instructions and a round-trip option.
- **Review:** a language model extracts the address from each line. The app first matches it to a fixed catalogue of 9 demo locations. If there is no match, it looks the address up with Nominatim (OpenStreetMap), limited to a Hyderabad bounding box. Geocoded points are approximate, not verified, and are labelled as such. The manager confirms the result before anything is optimized.
- **Result:** VROOM chooses the order, using road travel costs from Valhalla.

**Scope.** One vehicle, one depot, 1 to 8 stops, all in Hyderabad. The depot is chosen from a catalogue of 9 approximate demo locations. Each delivery is matched to that catalogue first, then looked up with Nominatim inside a Hyderabad bounding box. Geocoded points are approximate, not verified. There is no live traffic, no time windows and no vehicle capacity. These limits are also shown in the app.

## Setup and run
Tested on Windows with Git 2.56.0, Node v22.14.0, npm 10.9.2, Python 3.13.5 and Docker 29.8.2.

**1. Environment files** (from the root folder)

    copy .env.example .env
    copy backend\.env.example backend\.env

Then open `backend\.env` and set `GEMINI_API_KEY` to your own key and `GEMINI_MODEL` to a model your key can use (tested with gemini-3.5-flash and gemini-3.5-flash-lite). Never commit `backend\.env`.

For address lookup, set `NOMINATIM_USER_AGENT` to the app name plus the public repository URL, for example `LogiTrack-assessment-demo (https://github.com/Kaganya04/LogiTrack)`. Do not put a personal email in it. `GEOCODER_ENABLED` (default `true`) turns lookup on or off. Geocoding stays off until the User-Agent is set to a real value. Until then, only catalogue addresses resolve.

**2. Road engines** (Docker Desktop must be running)

    docker compose up -d valhalla
    docker compose logs -f valhalla

The first start downloads the Southern India road extract and builds routing tiles. On the test laptop (7.6 GB RAM, Docker limited to 4 GB) the tile build took about 12 minutes after the download. Wait until the log says the service has started, then check:

    curl.exe -i http://127.0.0.1:8002/status
    docker compose up -d vroom

**3. Backend** (second terminal)

    cd backend
    py -3.13 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python -m uvicorn app.main:app --reload --port 8000

**4. Frontend** (third terminal)

    cd frontend
    npm install
    npm run dev

Open http://localhost:5173.

**Engine checks** (from `backend`, environment active)

    python scripts/check_valhalla.py
    python scripts/check_vroom.py

## Example input
Depot: HITEC City hub, return to depot ticked.

    Madhapur
    Kondapur, Hyderabad
    Gachibowli
    Jubilee Hills
    Ayyappa Society

Observed result: order D1 Madhapur, D4 Jubilee Hills, D5 Ayyappa Society, D2 Kondapur, D3 Gachibowli, then back to the depot. Estimated 23.5 km and 66 minutes of driving.

A second browser check, with gemini-3.5-flash-lite, mixed catalogue and geocoded stops:

    Madhapur
    Hitec City Metro Station
    Charminar

Observed result: Madhapur matched the catalogue, and the other two were geocoded and marked approximate. Each stop was visited once, for an estimated 42.7 km and 93 minutes of driving on a round trip.

## Architecture
- **React (Vite)** handles input, review and result screens.
- **FastAPI** validates requests and coordinates the Python modules.
- `app/schemas.py` defines request and response shapes. It rejects zero or nine deliveries, duplicate delivery ids, unknown fields and non-boolean round-trip values.
- `app/preprocessing.py` cleans whitespace and enforces limits.
- `app/locations.py` loads the catalogue and matches addresses exactly on normalized names and aliases.
- `app/geocoding.py` looks up addresses that are not in the catalogue with Nominatim. It is limited to the Hyderabad bounding box, sends at most one request per second with an identifying User-Agent, and keeps an in-memory cache. Address text is never logged.
- `app/llm.py` asks the model for address text only, checks the answer, then resolves each address through the catalogue first and the geocoder second.
- `app/routing.py` is an adapter that turns confirmed deliveries (catalogue ids or coordinates) into a VROOM request and turns the answer back into app data.
- `app/logging_config.py` adds a request id to every log line.
- **VROOM** chooses the delivery order. **Valhalla** supplies road travel estimates from OpenStreetMap data.

API:
- `GET /api/locations` lists supported locations.
- `POST /api/parse` takes delivery lines (`id`, `text`) and optional instructions. For each delivery it returns the extracted address, `location_id`, display address, `lat`/`lng`, and a `source` field (`catalogue`, `geocoded` or `none`), plus clarification notes. If the geocoder is unavailable, unmatched deliveries get a clarification note, not an error.
- `POST /api/optimize` takes a depot, a round-trip flag and confirmed deliveries. Each delivery has an `id` and either a `location_id` or both `lat` and `lng`, never both forms. Coordinates must be inside the Hyderabad box. It returns the ordered ids, total distance in km, driving time in minutes and the assumptions.

## Decisions and assumptions
- **Catalogue first, then geocoding.** Addresses are matched to the 9-location catalogue first, because it is deterministic and needs no outside service. Only unmatched addresses go to Nominatim (OpenStreetMap). Lookups are limited to a Hyderabad bounding box, rate-limited to one request per second and cached, and they send an identifying User-Agent taken from `.env`. `GEOCODER_ENABLED` switches lookup off. Catalogue points and geocoded points are both approximate, not verified customer addresses.
- **Exact catalogue matching.** Partial or misspelled names are never fuzzy-matched to the catalogue, because a wrong guess would send the van to the wrong place. Those addresses go to the geocoder instead, and its result is shown as approximate for the manager to confirm.
- **The model never supplies coordinates.** It only extracts address text. The backend checks that the model returns every delivery id exactly once, then resolves each address through the catalogue or the geocoder.
- **The manager confirms the addresses** before optimization, and any change to the input clears the review and the route.
- **Time constraints are not supported.** If the instructions mention a time, the app says so and asks the manager to acknowledge it before optimizing.
- **VROOM and Valhalla instead of a custom solver.** The adapter converts ids, coordinate order (VROOM uses longitude then latitude) and units (metres to km, seconds to minutes), and rejects any result that is missing a delivery or repeats one.
- **Driving time** excludes waiting and service time. The van uses the Valhalla `auto` profile, with no height or weight restrictions.
- **Road data** is the Geofabrik Southern Zone extract, which covers Hyderabad. It is a large download.
- **Python 3.13.5** is the tested version.
- **Model choice.** Two model names that appeared in the account's model list returned 404 when called, so a model was chosen by testing it directly. The app was tested with gemini-3.5-flash and gemini-3.5-flash-lite, and the geocoded browser check above used gemini-3.5-flash-lite. Model availability and free quotas change, so check what your key can use.
- **Logging** records the request id, endpoint, status, duration and outcome. It does not record API keys or raw address text.
- **Pinned Valhalla image.** compose.yaml pins the Valhalla image by digest, the same image used to build the tiles for the tests recorded here. Limitation: the tiles are built on first start, and the time varies by machine.

## Coding standards
Descriptive names, snake_case in Python and PascalCase for React components. Pydantic schemas at the API boundary. Small functions. External calls (VROOM, the model, Nominatim) are isolated so the cleaning and validation code can be tested without them. No secrets in source code, and the API key stays on the backend.

## Tests
Run from `backend` with the environment active:

    python -m pytest -q

90 tests pass. The model, the geocoder and the routing engine are mocked in unit tests, so they need no Docker, API key or network access. Live checks and browser checks, with what was observed, are recorded in `docs/test-results.md`. Frontend checks: `npm run lint` and `npm run build` both pass.

## Limitations
- Geocoding uses the public Nominatim service and OpenStreetMap data:
  - OpenStreetMap coverage of Indian addresses is uneven.
  - House numbers often resolve only to a street or area.
  - A match can be a nearby shop or landmark rather than the intended address.
  - The public service can block or withdraw access.
  - The cache is in memory and is lost on restart.
  - The one-request-per-second limit assumes a single backend process.
  - Lookups are not suitable for real customer addresses.
- The depot must be one of the 9 catalogue locations.
- No live traffic, time windows, vehicle capacity or multiple vehicles. Maximum 8 deliveries.
- Distances and times are routing estimates between approximate points.
- VROOM is a heuristic solver, so the order is good but not guaranteed to be globally optimal.
- Extraction depends on a hosted model, which can fail or hit a rate limit. The app then shows a readable message and does not guess.
- Concurrent-user performance was not measured, so no claim is made about 100 simultaneous users.
- A development stub for the model call exists (`LLM_STUB`). It is off by default, returns simulated answers and labels them as such, and must stay off for real use.

## AI usage
AI tools were used in two different ways.

**In the application:** the app calls a Gemini model (tested with gemini-3.5-flash and gemini-3.5-flash-lite) to extract address text from delivery lines. Its output is validated before use, and the model never provides coordinates.

**In development:** I used Claude (Anthropic) as an assistant while building this project: for planning the architecture, drafting backend and React code, debugging setup and runtime problems, and explaining concepts. It touched most files in the repository.

What I did myself and checked:
- I ran every command, installed and configured the tools and engines, and set up the environment.
- I ran the automated tests and the live engine checks, and I tested the app in the browser, including invalid input, a misspelled address, an unsupported time instruction, editing after review, a stopped backend and a model quota error. The results are in `docs/test-results.md`.
- I debugged real problems on my machine: a port conflict from an old server, a model name that returned 404, ignored files that were not being excluded, and lint errors.
- I chose which model to use after testing which ones my key could call.

I also used Claude Code at the end for small cleanups: removing unused template files and pinning the Valhalla image. I reviewed and approved each change and ran lint and build myself.

Claude Code also helped with the geocoding work, both the backend lookup and the frontend changes. I reviewed the code, ran it and tested it myself.

