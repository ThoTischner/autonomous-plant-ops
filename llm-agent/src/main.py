from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.analyze import router as analyze_router

app = FastAPI(title="LLM Agent - Autonomous Plant Ops")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "llm-agent"}
