import time
from fastapi import FastAPI
from model.error_event import ErrorEvent

# from huey import SqliteHuey
from tasks import add
import logging


api_app = FastAPI()
log = logging.getLogger(__name__)


@api_app.get("/")
async def root():
    task = add(1, 2)
    return {"message": "Hello World " + str(task.id)}


@api_app.post("/errorEvent")
async def capture_error_event(errorEvent: ErrorEvent):
    """
    Endpoint to handle error events.
    """
    log.info("Received error event:", errorEvent)
    task = add(1, 2)
    return {
        "correlation_id": task.id,
        "stack_trace": errorEvent.stack_trace,
    }
