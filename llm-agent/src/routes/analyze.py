from fastapi import APIRouter

from ..agent import AnalysisAgent
from ..models import AnalysisRequest, AnalysisResponse

router = APIRouter()

agent = AnalysisAgent()


@router.post("/agent/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest) -> AnalysisResponse:
    return await agent.analyze(request)
