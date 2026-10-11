# LogiTrack

Delivery route planning for one light van, built with React, FastAPI, VROOM and Valhalla.

## Overview
To be completed

## Setup and run
Tested on Windows with:
- Git 2.56.0
- Node v22.14.0 and npm 10.9.2
- Python 3.13.5
- Docker 29.8.2

Frontend:
    cd frontend
    npm install
    npm run dev

Backend (in a second terminal):
    cd backend
    py -3.13 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python -m uvicorn app.main:app --reload --port 8000

## Example input
To be completed

## Architecture
- React (Vite): the browser interface for entering deliveries and viewing the route.
- FastAPI: checks requests and coordinates the Python functions.
- The LLM, location catalogue, VROOM and Valhalla are added in later steps.

## Decisions and assumptions
- Python 3.13 instead of the guide's 3.12. Reason: it was already installed. Limitation: not the version the guide names.

## Coding standards
To be completed

## Tests
See docs/test-results.md.

## Limitations
To be completed

## AI usage
To be completed