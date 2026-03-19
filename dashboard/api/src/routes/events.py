import asyncio
import json
from typing import Optional

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from ..models import Event, EventType
from ..store import EventStore

router = APIRouter(prefix="/events", tags=["events"])
store = EventStore()


@router.post("")
async def create_event(payload: dict):
    event = Event(**payload)
    await store.add(event)
    return {"status": "ok", "event_id": event.id}


@router.get("")
async def list_events(
    limit: int = 100,
    event_type: Optional[EventType] = None,
):
    if event_type is not None:
        return store.get_by_type(event_type, limit=limit)
    return store.get_all(limit=limit)


@router.get("/stream")
async def stream_events(request: Request):
    queue = store.subscribe()

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event: Event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield {
                        "event": event.event_type.value,
                        "data": event.model_dump_json(),
                    }
                except asyncio.TimeoutError:
                    # Send keepalive comment
                    yield {"comment": "keepalive"}
        finally:
            store.unsubscribe(queue)

    return EventSourceResponse(event_generator())
