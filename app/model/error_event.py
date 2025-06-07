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
    user_resolution_acceptance: str | None = None # e.g., "LIKE", "DISLIKE"
    occurrence_count: int = 1
    created_ts: datetime | None = None
    updated_ts: datetime | None = None
    # stacktrace_vec TODO
    error_timestamp: datetime
    user_feedback: str | None = None
    origin_line_number: int
    origin_class: str | None = None
    source_branch: str | None = None
    affected_jira_ids: str | None = None # Comma-separated list of Jira IDs