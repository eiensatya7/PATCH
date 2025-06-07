import logging
from typing import Optional

from app.dao.error_event_dao import ErrorEventDao
from app.model.error_event import ErrorEvent


class ErrorEventService:
    """
    Service class for managing ErrorEvent operations.

    This class provides methods to create and retrieve ErrorEvent instances.
    It interacts with the data access layer to perform these operations.
    """

    def __init__(self):
        """
        Initialize the service with a DAO instance for database operations.
        """
        self.log = logging.getLogger(__name__)
        self.error_event_dao = ErrorEventDao()

    def get_error_event_by_id(self, event_id: int) -> ErrorEvent | None:
        """
        Retrieve an ErrorEvent by its ID.

        Args:
            event_id (int): The ID of the ErrorEvent to retrieve.

        Returns:
            ErrorEvent | None: The ErrorEvent if found, otherwise None.
        """
        self.log.info(f"Retrieving error event with id {event_id}")
        error_event = self.error_event_dao.find_by_id(event_id)
        if error_event:
            self.log.info(f"Error event found: {error_event}")
        else:
            self.log.warning(f"No error event found with id {event_id}")
        return error_event

    def get_error_events_by_lob(self, lob: str) -> list[ErrorEvent]:
        """
        Retrieve all ErrorEvents for a specific LOB.

        Args:
            lob (str): The LOB name to filter by.

        Returns:
            list[ErrorEvent]: A list of ErrorEvents for the specified LOB.
        """
        self.log.info(f"Retrieving error events for lob: {lob}")
        error_events = self.error_event_dao.find_by_lob(lob)
        self.log.info(f"Found {len(error_events)} error event(s) for lob: {lob}")
        return error_events

    def create_error_event(self, error_event: ErrorEvent, lob_app_id: int, event_state: str) -> ErrorEvent:
        """
        Create a new ErrorEvent.

        Args:
            error_event (ErrorEvent): The ErrorEvent to create.
            lob_app_id (int): The LOB application ID to associate with this error event.
            event_state (str): The initial state of the error event.

        Returns:
            ErrorEvent: The created ErrorEvent with updated ID and timestamps.
        """
        self.log.info("Creating new error event")
        
        # Set the database-specific fields
        error_event.lob_app_id = lob_app_id
        error_event.event_state = event_state
        
        saved_error_event = self.error_event_dao.save_error_event(error_event)
        self.log.info(f"Error event created successfully with id {saved_error_event.event_id}")
        return saved_error_event

    def approve_error_event(self, event_id: int) -> bool:
        """
        Approve an error event by changing its state from PENDING_APPROVAL to PROCESSING.

        Args:
            event_id (int): The ID of the error event to approve.

        Returns:
            bool: True if the approval was successful, False otherwise.
        """
        self.log.info(f"Approving error event with id {event_id}")
        
        # First check if the event exists and is in PENDING_APPROVAL state
        error_event = self.error_event_dao.find_by_id(event_id)
        if not error_event:
            self.log.warning(f"Error event with id {event_id} not found")
            return False
        
        if error_event.event_state != "PENDING_APPROVAL":
            self.log.warning(f"Error event with id {event_id} is not in PENDING_APPROVAL state. Current state: {error_event.event_state}")
            return False
        
        # Update the state to PROCESSING
        success = self.error_event_dao.update_event_state(event_id, "PROCESSING")
        if success:
            self.log.info(f"Error event {event_id} approved and moved to PROCESSING state")
            # TODO: Submit to processing queue
            self.log.info(f"Error event {event_id} submitted to processing queue")
        else:
            self.log.error(f"Failed to approve error event {event_id}")
        
        return success
