# LogiTrack

LogiTrack helps a logistics manager plan the delivery order for one light van. The manager types delivery addresses in plain language, reviews what the system understood, and gets an ordered route with estimated road distance and driving time.

## Overview
- **Input:** up to 8 delivery lines, a depot, optional instructions and a round-trip option.
- **Review:** a language model extracts the address from each line. The app then matches it to a fixed catalogue of demo locations. The manager confirms the result before anything is optimized.
- **Result:** VROOM chooses the order, using road travel costs from Valhalla.

**Scope.** One vehicle, one depot, 1 to 8 stops. Only a catalogue of 9 approximate demo locations in Hyderabad is supported. There is no live traffic, no time windows and no vehicle capacity. These limits are also shown in the app.

## Setup and run
Tested on Windows with Git 2.56.0, Node v22.14.0, npm 10.9.2, Python 3.13.5 and Docker 29.8.2.

**1. Environment files** (from the root folder)

    copy .env.example .env
    copy backend\.env.example backend\.env

Then open `backend\.env` and set `GEMINI_API_KEY` to your own key and `GEMINI_MODEL` to a model your key can use (tested with gemini-3.5-flash-lite). Never commit `backend\.env`.

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

## Architecture
- **React (Vite)** handles input, review and result screens.
- **FastAPI** validates requests and coordinates the Python modules.
- `app/schemas.py` defines request and response shapes. It rejects zero or nine deliveries, duplicate delivery ids, unknown fields and non-boolean round-trip values.
- `app/preprocessing.py` cleans whitespace and enforces limits.
- `app/locations.py` loads the catalogue and matches addresses exactly on normalized names and aliases.
- `app/llm.py` asks the model for address text only, then checks the answer.
- `app/routing.py` is an adapter that turns confirmed deliveries into a VROOM request and turns the answer back into app data.
- `app/logging_config.py` adds a request id to every log line.
- **VROOM** chooses the delivery order. **Valhalla** supplies road travel estimates from OpenStreetMap data.

API:
- `GET /api/locations` lists supported locations.
- `POST /api/parse` takes delivery lines (`id`, `text`) and optional instructions. It returns the extracted address, the matched location and clarification notes.
- `POST /api/optimize` takes a depot, a round-trip flag and confirmed deliveries (`id`, `location_id`). It returns the ordered ids, total distance in km, driving time in minutes and the assumptions.

## Decisions and assumptions
- **Fixed catalogue instead of geocoding.** Reason: it keeps coordinates deterministic and avoids an extra service. Limitation: addresses outside the 9 demo locations are rejected, and the coordinates are approximate demo points, not verified customer addresses.
- **Exact matching only.** Partial or misspelled names are never guessed, because a wrong guess would send the van to the wrong place.
- **The model never supplies coordinates.** It only extracts address text. The backend checks that the model returns every delivery id exactly once, then resolves each address through the catalogue.
- **The manager confirms the addresses** before optimization, and any change to the input clears the review and the route.
- **Time constraints are not supported.** If the instructions mention a time, the app says so and asks the manager to acknowledge it before optimizing.
- **VROOM and Valhalla instead of a custom solver.** The adapter converts ids, coordinate order (VROOM uses longitude then latitude) and units (metres to km, seconds to minutes), and rejects any result that is missing a delivery or repeats one.
- **Driving time** excludes waiting and service time. The van uses the Valhalla `auto` profile, with no height or weight restrictions.
- **Road data** is the Geofabrik Southern Zone extract, which covers Hyderabad. It is a large download.
- **Python 3.13.5** is the tested version.
- **Model choice.** Two model names that appeared in the account's model list returned 404 when called, so a model was chosen by testing it directly. Model availability and free quotas change, so check what your key can use.
- **Logging** records the request id, endpoint, status, duration and outcome. It does not record API keys or raw address text.

## Coding standards
Descriptive names, snake_case in Python and PascalCase for React components. Pydantic schemas at the API boundary. Small functions. External calls (VROOM, the model) are isolated so the cleaning and validation code can be tested without them. No secrets in source code, and the API key stays on the backend.

## Tests
Run from `backend` with the environment active:

    python -m pytest -q

46 tests pass. The model and the routing engine are mocked in unit tests, so they need neither Docker nor an API key. Live checks and browser checks, with what was observed, are recorded in `docs/test-results.md`. Frontend checks: `npm run lint` and `npm run build` both pass.

## Limitations
- Only 9 demo locations. No arbitrary street-address geocoding.
- No live traffic, time windows, vehicle capacity or multiple vehicles. Maximum 8 deliveries.
- Distances and times are routing estimates between approximate points.
- VROOM is a heuristic solver, so the order is good but not guaranteed to be globally optimal.
- Extraction depends on a hosted model, which can fail or hit a rate limit. The app then shows a readable message and does not guess.
- Concurrent-user performance was not measured, so no claim is made about 100 simultaneous users.

## AI usage
AI tools were used in two different ways.

**In the application:** the app calls a Gemini model (gemini-3.5-flash-lite when tested) to extract address text from delivery lines. Its output is validated before use, and the model never provides coordinates.

**In development:** I used Claude (Anthropic) as an assistant while building this project: for planning the architecture, drafting backend and React code, debugging setup and runtime problems, and explaining concepts. It touched most files in the repository.

What I did myself and checked:
- I ran every command, installed and configured the tools and engines, and set up the environment.
- I ran the automated tests and the live engine checks, and I tested the app in the browser, including invalid input, a misspelled address, an unsupported time instruction, editing after review, a stopped backend and a model quota error. The results are in `docs/test-results.md`.
- I debugged real problems on my machine: a port conflict from an old server, a model name that returned 404, ignored files that were not being excluded, and lint errors.
- I chose which model to use after testing which ones my key could call.

[Edit this section so every sentence is true for you, and be ready to explain any file in the repository.]
