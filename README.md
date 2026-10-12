# LogiTrack

Delivery route planning for one light van, built with React (Vite), FastAPI, VROOM and Valhalla.

## Overview
To be completed

## Setup and run
Tested on Windows with Git 2.56.0, Node v22.14.0, npm 10.9.2, Python 3.13.5 and Docker 29.8.2.

Road engines (Docker Desktop must be running), from the root folder:

    docker compose up -d valhalla
    docker compose logs -f valhalla
    curl.exe -i http://127.0.0.1:8002/status
    docker compose up -d vroom

Copy .env.example to .env first. It holds the map download URL, not a secret.

Backend, in a second terminal:

    cd backend
    py -3.13 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python -m uvicorn app.main:app --reload --port 8000

Frontend, in a third terminal:

    cd frontend
    npm install
    npm run dev

Engine checks, from backend with the environment active:

    python scripts/check_valhalla.py
    python scripts/check_vroom.py

## Example input
To be completed

## Architecture
- React (Vite): the browser interface for entering deliveries and viewing the route.
- FastAPI: checks requests and coordinates the Python functions.
- Valhalla: supplies road travel estimates from OpenStreetMap data.
- VROOM: chooses the delivery order, using Valhalla for travel costs.
- The LLM and the location catalogue are added in later steps.

## Decisions and assumptions
- Python 3.13.5 is the tested version. Reason: it was already installed and all dependencies work on it. Limitation: older Python versions were not tested.
- Road data is the Geofabrik Southern Zone extract of India. Reason: it covers Hyderabad and comes from a regularly updated public source. Limitation: a large download, and tile building took about 12 minutes on a laptop with 7.6 GB RAM using Docker limited to 4 GB.
- The van uses the Valhalla auto profile, so it is treated as a light van with no height or weight restrictions.
- Valhalla and VROOM run in Docker. VROOM reaches Valhalla through the Compose service name valhalla, not localhost.

## Coding standards
To be completed

## Tests
Live engine checks passed for 5 and 8 stops, round trip and open trip. See docs/test-results.md.

## Limitations
No live traffic. Road travel estimates only. One vehicle. No time windows or vehicle capacity.

## AI usage
To be completed

