from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.events import router as events_router

app = FastAPI(title="Autonomous Plant Ops - Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router)


@app.get("/health")
async def health():
    return {"status": "healthy"}
