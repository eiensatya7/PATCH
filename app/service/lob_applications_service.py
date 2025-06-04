import logging

from app.dao.lob_application_dao import LobApplicationDao
from app.model.lob_application import LobApplication


class LobApplicationsService:
    """
    Service class for managing LobApplication operations.

    This class provides methods to create and retrieve LobApplication instances.
    It interacts with the data access layer to perform these operations.
    """

    def __init__(self):
        """
        Initialize the service with a DAO instance for database operations.
        """
        self.log = logging.getLogger(__name__)
        self.lob_application_dao = LobApplicationDao()

    def get_lob_application_by_id(self, lob_app_id: int) -> LobApplication | None:
        """
        Retrieve a LobApplication by its ID.

        Args:
            lob_app_id (int): The ID of the LobApplication to retrieve.

        Returns:
            LobApplication | None: The LobApplication if found, otherwise None.
        """
        self.log.info(f"Retrieving lob application with id {lob_app_id}")
        lob_application = self.lob_application_dao.find_by_id(lob_app_id)
        if lob_application:
            self.log.info(f"Lob application found: {lob_application}")
        else:
            self.log.warning(f"No lob application found with id {lob_app_id}")
        return lob_application

    def get_lob_applications_by_lob(self, lob: str) -> list[LobApplication]:
        """
        Retrieve all LobApplications for a specific LOB.

        Args:
            lob (str): The LOB name to filter by.

        Returns:
            list[LobApplication]: A list of LobApplications for the specified LOB.
        """
        self.log.info(f"Retrieving lob applications for lob: {lob}")
        lob_applications = self.lob_application_dao.find_by_lob(lob)
        self.log.info(f"Found {len(lob_applications)} lob application(s) for lob: {lob}")
        return lob_applications

    def create_lob_application(self, lob_application: LobApplication) -> LobApplication:
        """
        Create a new LobApplication.

        Args:
            lob_application (LobApplication): The LobApplication to create.

        Returns:
            LobApplication: The created LobApplication with updated ID and timestamps.
        """
        self.log.info("Creating new lob application")
        saved_lob_application = self.lob_application_dao.save(lob_application)
        self.log.info(f"Lob application created successfully with id {saved_lob_application.lob_app_id}")
        return saved_lob_application

    def get_lob_application_by_lob_app_and_env(self, lob: str, application_name: str, environment: str) -> LobApplication | None:
        """
        Retrieve a LobApplication by LOB, application name, and environment.

        Args:
            lob (str): The LOB name.
            application_name (str): The application name.
            environment (str): The environment.

        Returns:
            LobApplication | None: The LobApplication if found, otherwise None.
        """
        self.log.info(f"Retrieving lob application for lob: {lob}, application: {application_name}, environment: {environment}")
        lob_application = self.lob_application_dao.find_by_lob_application_and_environment(lob, application_name, environment)
        if lob_application:
            self.log.info(f"Lob application found: {lob_application}")
        else:
            self.log.warning(f"No lob application found for lob: {lob}, application: {application_name}, environment: {environment}")
        return lob_application


