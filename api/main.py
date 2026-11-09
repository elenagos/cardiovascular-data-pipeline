from fastapi import FastAPI

from api.routers import health, patients, prediction

app = FastAPI(
    title="CardioPulse API",
    version="0.1.0",
)


app.include_router(
    health.router
)


app.include_router(
    patients.router
)


app.include_router(
    prediction.router
)