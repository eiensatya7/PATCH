import time
from fastapi import FastAPI
from model.error_event import ErrorEvent
from model.onboard_request import OnboardRequest

# from huey import SqliteHuey
from tasks import add
import logging

api_app = FastAPI()
log = logging.getLogger(__name__)


@api_app.get("/")
async def root():
    task = add(1, 2)
    return {"message": "Hello World " + str(task.id)}


# Onboard New Lob application
@api_app.post("/lob-applications")
async def onboard_lob_applications(onboard_request: OnboardRequest):
    """
    Endpoint to Onboard new lob application.
    """
    log.info("Received onboardRequest:", onboard_request)


@api_app.post("/error-events")
async def capture_error_event(error_event: ErrorEvent):
    """
    Endpoint to handle error events.
    """
    # Get lob_application by lob, application_name and environment
    # if lob_application is None: Skip event
    # if lob_application.auto_resolve is FALSE, save Error Event with state "PENDING_APPROVAL"
    # if lob_application.auto_resolve is TRUE, save Error Event with state "PROCESSING" and submit to the processing queue

    log.info("Received error event:", error_event)
    task = add(1, 2)
    return {
        "correlation_id": task.id,
        "stack_trace": error_event.stack_trace,
    }


@api_app.get("/error-events")
async def get_error_events(lob: str = None):
    """
    Endpoint to retrieve error events, optionally filtered by lob.
    """
    log.info(f"Retrieving error events for lob: {lob}")
    # Here you would typically query your database or data store, filtering by lob if provided
    return {"message": f"This would return a list of error events{f' for lob {lob}' if lob else ''}."}


@api_app.delete("/error-events/{event_id}")
async def cancel_error_events(event_id: int):
    """
    Endpoint to cancel error events, optionally filtered by lob.
    """
    log.info(f"Deleting error events for event_id: {event_id}")
    # Here you would typically perform a delete operation in your database or data store
    return {"message": f"Cancelled error events{f' for event_id {event_id}' if event_id else ''}."}



@api_app.post("/error-events/{event_id}/approve")
async def approve_error_event(event_id: int):
    """
    Endpoint to approve error event processing by event_id.
    """
    # Check if event_id exists in the database & is in "PENDING_APPROVAL" state
    # If it exists, update its state to "PROCESSING" and submit to the processing queue
    log.info(f"Approving error event with event_id: {event_id}")
    # Here you would typically update the event's state in your database
    return {"message": f"Approved error event with event_id {event_id}."}