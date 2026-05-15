from fastapi import APIRouter
from pydantic import BaseModel

from ..prompts import (
    DEFAULT_SYSTEM_PROMPT,
    get_system_prompt,
    is_default_prompt,
    reset_system_prompt,
    set_system_prompt,
)

router = APIRouter(prefix="/agent/prompt", tags=["prompt"])


class PromptBody(BaseModel):
    prompt: str


class PromptInfo(BaseModel):
    prompt: str
    is_default: bool
    default_prompt: str


def _info() -> PromptInfo:
    return PromptInfo(
        prompt=get_system_prompt(),
        is_default=is_default_prompt(),
        default_prompt=DEFAULT_SYSTEM_PROMPT,
    )


@router.get("", response_model=PromptInfo)
async def read_prompt() -> PromptInfo:
    return _info()


@router.put("", response_model=PromptInfo)
async def update_prompt(body: PromptBody) -> PromptInfo:
    set_system_prompt(body.prompt)
    return _info()


@router.post("/reset", response_model=PromptInfo)
async def reset_prompt() -> PromptInfo:
    reset_system_prompt()
    return _info()
