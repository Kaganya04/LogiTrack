from fastapi import FastAPI

app = FastAPI(title="LogiTrack")


@app.get("/api/health")
def health():
    return {"status": "ok"}