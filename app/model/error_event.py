from pydantic import BaseModel



class ErrorEvent(BaseModel):
    """
    Represents an error event with a message and a stack trace.
    """

    correlation_id: str
    stack_trace: str
    lob: str
    application_name: str
    environment: str
    timestamp: str

    def __str__(self) -> str:
        return (
            f"ErrorEvent(correlation_id={self.correlation_id}, "
            f"stack_trace={self.stack_trace}, lob={self.lob}, "
            f"application_name={self.application_name}, "
            f"environment={self.environment}, timestamp={self.timestamp})"
        )
