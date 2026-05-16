from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import actions, equipment, scenarios, sensors
from .simulator import simulator

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(simulator.run())
    yield
    simulator.stop()
    task.cancel()
    # Await the cancelled background task, swallowing its CancelledError.
    await asyncio.gather(task, return_exceptions=True)


app = FastAPI(title="Sensor Simulator", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sensors.router)
app.include_router(actions.router)
app.include_router(scenarios.router)
app.include_router(equipment.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "sensor-simulator"}
