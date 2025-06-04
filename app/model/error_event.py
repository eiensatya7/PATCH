from pydantic import BaseModel
from typing import Optional


class ErrorEvent(BaseModel):
    """
    Represents an error event with a message and a stack trace.
    """

    # Fields from the request
    correlation_id: str
    stack_trace: str
    lob: str
    application_name: str
    environment: str
    timestamp: str
    
    # Database fields
    event_id: Optional[int] = None
    lob_app_id: Optional[int] = None
    event_state: Optional[str] = "NEW"
    span_id: Optional[str] = None
    stacktrace: Optional[str] = None  # Database field name for stack_trace
    origin_method: Optional[str] = None
    resolution: Optional[str] = None
    pull_request_url: Optional[str] = None
    confidence: Optional[str] = None
    resolution_acceptance_state: Optional[str] = None
    occurrence_count: Optional[int] = 1
    created_ts: Optional[str] = None
    updated_ts: Optional[str] = None

    def __str__(self) -> str:
        return (
            f"ErrorEvent(event_id={self.event_id}, "
            f"correlation_id={self.correlation_id}, "
            f"stack_trace={self.stack_trace}, lob={self.lob}, "
            f"application_name={self.application_name}, "
            f"environment={self.environment}, timestamp={self.timestamp}, "
            f"event_state={self.event_state})"
        )
