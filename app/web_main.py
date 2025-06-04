import time
import logging
from fastapi import FastAPI, HTTPException, status
from dotenv import load_dotenv

from app.model.lob_application import LobApplication
from app.service.lob_applications_service import LobApplicationsService
from app.model.error_event import ErrorEvent
from app.service.error_event_service import ErrorEventService
from app.model.onboard_request import OnboardRequest
from app.tasks import add
import uvicorn


class WebMain:
    """
    Main web application class that encapsulates FastAPI app and its routes.
    """
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        self.api_app = FastAPI()
        self.log = logging.getLogger(__name__)
        self.lob_service = LobApplicationsService()
        self.error_event_service = ErrorEventService()
        self._setup_routes()
    
    def _setup_routes(self):
        """
        Setup all API routes for the FastAPI application.
        """
        self.api_app.get("/")(self.root)
        self.api_app.post("/lob-applications")(self.onboard_lob_applications)
        self.api_app.get("/lob-applications")(self.get_lob_applications_by_lob)
        self.api_app.get("/lob-applications/{lob_application_id}")(self.get_lob_application_by_id)
        self.api_app.post("/error-events")(self.capture_error_event)
        self.api_app.get("/error-events")(self.get_error_events)
        self.api_app.delete("/error-events/{event_id}")(self.cancel_error_events)
        self.api_app.post("/error-events/{event_id}/approve")(self.approve_error_event)
    
    async def root(self):
        """
        Root endpoint that returns a hello world message.
        """
        task = add(1, 2)
        return {"message": "Hello World " + str(task.id)}
    
    def onboard_lob_applications(self, lob_application: LobApplication):
        """
        Endpoint to Onboard new lob application.
        """
        self.log.info("Received lob_application onboarding request:", lob_application)
        created_lob_application = self.lob_service.create_lob_application(lob_application)
        self.log.info("Created lob_application:", created_lob_application)
        return created_lob_application
    
    async def get_lob_applications_by_lob(self, lob: str):
        """
        Endpoint to get all LOB applications by LOB.
        """
        self.log.info(f"Retrieving LOB applications for lob: {lob}")
        try:
            lob_applications = self.lob_service.get_lob_applications_by_lob(lob)
            self.log.info(f"Found {len(lob_applications) if lob_applications else 0} LOB applications for lob: {lob}")
            return lob_applications
        except Exception as e:
            self.log.error(f"Error retrieving LOB applications for lob {lob}: {str(e)}")
            raise
    
    async def get_lob_application_by_id(self, lob_application_id: int):
        """
        Endpoint to get a specific LOB application by lob_application_id.
        """
        self.log.info(f"Retrieving LOB application with id: {lob_application_id}")
        try:
            lob_application = self.lob_service.get_lob_application_by_id(lob_application_id)
            if lob_application is None:
                self.log.warning(f"LOB application with id {lob_application_id} not found")
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"LOB application with id {lob_application_id} not found"
                )
            self.log.info(f"Found LOB application with id: {lob_application_id}")
            return lob_application
        except Exception as e:
            self.log.error(f"Error retrieving LOB application with id {lob_application_id}: {str(e)}")
            raise
    
    async def capture_error_event(self, error_event: ErrorEvent):
        """
        Endpoint to handle error events.
        """
        # Get lob_application by lob, application_name and environment
        # if lob_application is None: Skip event
        # if lob_application.auto_resolve is FALSE, save Error Event with state "PENDING_APPROVAL"
        # if lob_application.auto_resolve is TRUE, save Error Event with state "PROCESSING" and submit to the processing queue

        self.log.info("Received error event:", error_event)
        
        try:
            # Get lob_application by lob, application_name and environment
            lob_application = self.lob_service.get_lob_application_by_lob_app_and_env(
                error_event.lob, 
                error_event.application_name, 
                error_event.environment
            )
            
            # If lob_application is None: Skip event
            if lob_application is None:
                self.log.warning(f"No LOB application found for lob={error_event.lob}, "
                               f"application={error_event.application_name}, "
                               f"environment={error_event.environment}. Skipping error event.")
                return {"message": "Error event skipped - no matching LOB application found"}
            
            # Determine the event state based on auto_resolve setting
            if lob_application.auto_resolve:
                # If auto_resolve is TRUE, save Error Event with state "PROCESSING" 
                event_state = "PROCESSING"
                self.log.info(f"Auto-resolve enabled for LOB application {lob_application.lob_app_id}. "
                            f"Setting error event state to PROCESSING")
            else:
                # If auto_resolve is FALSE, save Error Event with state "PENDING_APPROVAL"
                event_state = "PENDING_APPROVAL"
                self.log.info(f"Auto-resolve disabled for LOB application {lob_application.lob_app_id}. "
                            f"Setting error event state to PENDING_APPROVAL")
            
            # Create the error event
            created_error_event = self.error_event_service.create_error_event(
                error_event, 
                lob_application.lob_app_id, 
                event_state
            )
            
            # If auto_resolve is TRUE, submit to the processing queue
            if lob_application.auto_resolve:
                # TODO: Submit to processing queue
                self.log.info(f"Error event {created_error_event.event_id} submitted to processing queue")
            
            self.log.info(f"Error event successfully processed with ID: {created_error_event.event_id}")
            return {
                "message": "Error event captured successfully",
                "event_id": created_error_event.event_id,
                "event_state": created_error_event.event_state
            }
            
        except Exception as e:
            self.log.error(f"Error processing error event: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process error event: {str(e)}"
            )

    
    async def get_error_events(self, lob: str = None):
        """
        Endpoint to retrieve error events, optionally filtered by lob.
        """
        self.log.info(f"Retrieving error events for lob: {lob}")
        
        try:
            if lob:
                error_events = self.error_event_service.get_error_events_by_lob(lob)
                return error_events
            else:
                # TODO: Implement get_all_error_events if needed
                return {"message": "Please provide a 'lob' parameter to filter error events"}
                
        except Exception as e:
            self.log.error(f"Error retrieving error events for lob {lob}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve error events: {str(e)}"
            )
    
    async def cancel_error_events(self, event_id: int):
        """
        Endpoint to cancel error events, optionally filtered by lob.
        """
        self.log.info(f"Deleting error events for event_id: {event_id}")
        # Here you would typically perform a delete operation in your database or data store
        return {"message": f"Cancelled error events{f' for event_id {event_id}' if event_id else ''}."}
    
    async def approve_error_event(self, event_id: int):
        """
        Endpoint to approve error event processing by event_id.
        """
        self.log.info(f"Approving error event with event_id: {event_id}")
        
        try:
            # Check if event_id exists in the database & is in "PENDING_APPROVAL" state
            # If it exists, update its state to "PROCESSING" and submit to the processing queue
            success = self.error_event_service.approve_error_event(event_id)
            
            if success:
                return {"message": f"Approved error event with event_id {event_id}."}
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Error event with id {event_id} not found or not in PENDING_APPROVAL state"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            self.log.error(f"Error approving error event {event_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to approve error event: {str(e)}"
            )
    
    def get_app(self):
        """
        Return the FastAPI application instance.
        """
        return self.api_app
    
    def run(self, host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
        """
        Run the FastAPI application using uvicorn.
        """
        if reload:
            # Use import string for reload mode
            uvicorn.run("app.web_main:api_app", host=host, port=port, reload=reload)
        else:
            # Use the app instance directly when reload is disabled
            uvicorn.run(self.api_app, host=host, port=port, reload=reload)


# Create a global instance for backward compatibility
web_main = WebMain()
api_app = web_main.get_app()


if __name__ == "__main__":
    web_main.run()
