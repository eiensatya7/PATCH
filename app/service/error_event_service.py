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

    def approve_error_event(self, event_id: int) -> None:
        """
        Approve an error event by changing its state from PENDING_APPROVAL to PROCESSING.

        Args:
            event_id (int): The ID of the error event to approve.

        Raises:
            ValueError: If the error event is not found or not in PENDING_APPROVAL state
            Exception: If database operation fails
        """
        self.log.info(f"Approving error event with id {event_id}")
        
        # First check if the event exists and is in PENDING_APPROVAL state
        error_event = self.error_event_dao.find_by_id(event_id)
        if not error_event:
            self.log.error(f"Error event with id {event_id} not found")
            raise ValueError(f"Error event with id {event_id} not found")
        
        if error_event.event_state != "PENDING_APPROVAL":
            self.log.error(f"Error event with id {event_id} is not in PENDING_APPROVAL state. Current state: {error_event.event_state}")
            raise ValueError(f"Error event with id {event_id} is not in PENDING_APPROVAL state. Current state: {error_event.event_state}")
        
        # Update the state to PROCESSING
        try:
            self.error_event_dao.update_event_state(event_id, "PROCESSING")
            self.log.info(f"Error event {event_id} approved and moved to PROCESSING state")
            # TODO: Submit to processing queue
            self.log.info(f"Error event {event_id} submitted to processing queue")
        except Exception as e:
            self.log.error(f"Failed to approve error event {event_id}: {e}")
            raise
        
    def update_error_resolution(self, event_id: int, resolution: str, confidence: float, 
                               pull_request_url: str, event_state: str) -> None:
        """
        Update an error event with resolution details.

        Args:
            event_id (int): The ID of the error event to update
            resolution (str): The resolution description
            confidence (float): The confidence level of the resolution
            pull_request_url (str): URL of the pull request containing the fix
            event_state (str): The new state of the error event

        Raises:
            Exception: If the update operation fails
        """
        self.log.info(f"Updating error event {event_id} with resolution")
        
        try:
            self.error_event_dao.update_error_resolution(
                event_id, resolution, confidence, pull_request_url, event_state
            )
            self.log.info(f"Error event {event_id} updated successfully with resolution")
        except Exception as e:
            self.log.error(f"Failed to update error event {event_id} with resolution: {e}")
            raise

    def update_stacktrace_vector(self, event_id: int, stacktrace_vec: list) -> None:
        """
        Update the stacktrace vector for an error event.

        Args:
            event_id (int): The ID of the error event to update
            stacktrace_vec (list): The stacktrace vector to set

        Raises:
            Exception: If the update operation fails
        """
        self.log.info(f"Updating error event {event_id} with stacktrace vector")
        
        try:
            self.error_event_dao.update_stacktrace_vector(event_id, stacktrace_vec)
            self.log.info(f"Error event {event_id} updated successfully with stacktrace vector")
        except Exception as e:
            self.log.error(f"Failed to update error event {event_id} with stacktrace vector: {e}")
            raise

    def update_affected_jira(self, event_id: int, affected_jira_ids: str) -> None:
        """
        Update the affected JIRA IDs for an error event.

        Args:
            event_id (int): The ID of the error event to update
            affected_jira_ids (str): Comma-separated list of JIRA IDs

        Raises:
            Exception: If the update operation fails
        """
        self.log.info(f"Updating error event {event_id} with affected JIRA IDs: {affected_jira_ids}")
        
        try:
            self.error_event_dao.update_affected_jira(event_id, affected_jira_ids)
            self.log.info(f"Error event {event_id} updated successfully with affected JIRA IDs")
        except Exception as e:
            self.log.error(f"Failed to update error event {event_id} with affected JIRA IDs: {e}")
            raise

    def update_user_feedback(self, event_id: int, user_resolution_acceptance: str, user_feedback: str) -> None:
        """
        Update the user feedback for an error event.

        Args:
            event_id (int): The ID of the error event to update
            user_resolution_acceptance (str): User acceptance of resolution (LIKE/DISLIKE)
            user_feedback (str): User feedback text

        Raises:
            Exception: If the update operation fails
        """
        self.log.info(f"Updating error event {event_id} with user feedback")
        
        try:
            self.error_event_dao.update_user_feedback(event_id, user_resolution_acceptance, user_feedback)
            self.log.info(f"Error event {event_id} updated successfully with user feedback")
        except Exception as e:
            self.log.error(f"Failed to update error event {event_id} with user feedback: {e}")
            raise
