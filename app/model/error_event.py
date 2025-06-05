from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class ErrorEvent(BaseModel):
    """
    Represents an error event with a message and a stack trace.
    """

    # Fields from the request
    lob: str
    application_name: str
    environment: str

    # Database fields
    event_id: int | None = None
    lob_app_id: int | None = None
    event_state: str | None = "NEW"
    correlation_id: str
    span_id: str | None = None
    stacktrace: str
    origin_method: str
    resolution: str | None = None
    pull_request_url: str | None = None
    confidence: str | None = None
    resolution_acceptance_state: str | None = None
    occurrence_count: int = 1
    created_ts: datetime | None = None
    updated_ts: datetime | None = None
    error_timestamp: datetime

    def __str__(self) -> str:
        return (
            f"ErrorEvent(event_id={self.event_id}, "
            f"correlation_id={self.correlation_id}, "
            f"stack_trace={self.stacktrace}, lob={self.lob}, "
            f"application_name={self.application_name}, "
            f"environment={self.environment}, error_timestamp={self.error_timestamp}, "
            f"event_state={self.event_state})"
        )
