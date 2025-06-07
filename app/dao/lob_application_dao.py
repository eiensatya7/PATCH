import logging
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from typing import Optional
import os
import threading

from app.model.lob_application import LobApplication

log = logging.getLogger(__name__)


class LobApplicationDao:
    """
    Data Access Object for LobApplication entities.
    Handles database connections and CRUD operations for lob applications.
    """
    
    def __init__(self):
        """
        Initialize the DAO with database connection configuration and connection pool.
        """
        # Database connection configuration
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'your_database'),
            'user': os.getenv('DB_USER', 'your_username'),
            'password': os.getenv('DB_PASSWORD', 'your_password')
        }
        
        # Connection pool configuration
        self.pool_min_connections = int(os.getenv('DB_POOL_MIN', '1'))
        self.pool_max_connections = int(os.getenv('DB_POOL_MAX', '10'))
        
        # Connection pool instance and lock
        self._connection_pool = None
        self._pool_lock = threading.Lock()
        
        log.info("LobApplicationDao initialized")
    
    def _get_connection_pool(self):
        """
        Get or create the database connection pool (singleton pattern).
        
        Returns:
            psycopg2.pool.ThreadedConnectionPool: Connection pool instance
        """
        if self._connection_pool is None:
            with self._pool_lock:
                # Double-check locking pattern
                if self._connection_pool is None:
                    try:
                        self._connection_pool = psycopg2.pool.ThreadedConnectionPool(
                            minconn=self.pool_min_connections,
                            maxconn=self.pool_max_connections,
                            **self.db_config
                        )
                        log.info(f"Database connection pool created with {self.pool_min_connections}-{self.pool_max_connections} connections")
                    except psycopg2.Error as e:
                        log.error(f"Failed to create connection pool: {e}")
                        raise
        
        return self._connection_pool
    
    @contextmanager
    def _get_db_connection(self):
        """
        Context manager for getting a database connection from the pool.
        Automatically returns the connection to the pool when done.
        
        Yields:
            psycopg2.connection: Database connection from the pool
        """
        pool = self._get_connection_pool()
        connection = None
        
        try:
            connection = pool.getconn()
            if connection:
                log.debug("Retrieved connection from pool")
                yield connection
            else:
                raise psycopg2.Error("Failed to get connection from pool")
        except psycopg2.Error as e:
            log.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                pool.putconn(connection)
                log.debug("Returned connection to pool")
    
    @contextmanager
    def _get_db_cursor(self):
        """
        Context manager for database operations using connection pool.
        Automatically handles connection, cursor, commits, and cleanup.
        
        Yields:
            psycopg2.cursor: Database cursor for executing queries
        """
        with self._get_db_connection() as connection:
            cursor = None
            try:
                cursor = connection.cursor()
                yield cursor
                connection.commit()
                log.debug("Transaction committed successfully")
            except psycopg2.Error as e:
                connection.rollback()
                log.error(f"Database operation failed, transaction rolled back: {e}")
                raise
            finally:
                if cursor:
                    cursor.close()
    
    def save(self, lob_application: LobApplication) -> LobApplication:
        """
        Save a new lob application to the database.
        
        Args:
            lob_application (LobApplication): The lob application object to save
            
        Returns:
            LobApplication: The saved lob application object
            
        Raises:
            psycopg2.Error: If database operation fails
        """
        log.info(f"Saving lob application: {lob_application}")
        
        try:
            with self._get_db_cursor() as cursor:
                # INSERT query matching the lob_applications table schema
                insert_query = """
                    INSERT INTO lob_applications (
                        application_name, 
                        lob, 
                        auto_resolve, 
                        environment, 
                        git_remote_url, 
                        lookup_branch_pattern, 
                        filter_pii, 
                        notification_dls,
                        app_info_actuator_url,
                        jira_projects_url,
                        app_dynamics_url
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING lob_app_id, created_ts, updated_ts;
                """
                
                # Execute with actual lob_application attributes
                cursor.execute(insert_query, (
                    lob_application.application_name,
                    lob_application.lob,
                    lob_application.auto_resolve,
                    lob_application.environment,
                    lob_application.git_remote_url,
                    lob_application.lookup_branch_pattern,
                    lob_application.filter_pii,
                    lob_application.notification_dls,
                    lob_application.app_info_actuator_url,
                    lob_application.jira_projects_url,
                    lob_application.app_dynamics_url
                ))
                
                # Get the returned values (ID and timestamps)
                result = cursor.fetchone()
                if result:
                    lob_application.lob_app_id = result[0]
                    lob_application.created_ts = result[1].isoformat()
                    lob_application.updated_ts = result[2].isoformat()
                    log.info(f"Lob application saved successfully with ID: {lob_application.lob_app_id}")
                
            return lob_application
            
        except psycopg2.Error as e:
            log.error(f"Failed to save lob application: {e}")
            raise
    
    def find_by_id(self, lob_app_id: int) -> Optional[LobApplication]:
        """
        Retrieve a lob application by its ID.
        
        Args:
            lob_app_id (int): The ID of the lob application to retrieve
            
        Returns:
            Optional[LobApplication]: The lob application if found, None otherwise
        """
        try:
            with self._get_db_cursor() as cursor:
                select_query = """
                    SELECT lob_app_id, application_name, lob, auto_resolve, environment,
                           git_remote_url, lookup_branch_pattern, filter_pii,
                           created_ts, updated_ts, notification_dls, app_info_actuator_url,
                           jira_projects_url, app_dynamics_url
                    FROM lob_applications
                    WHERE lob_app_id = %s;
                """
                
                cursor.execute(select_query, (lob_app_id,))
                result = cursor.fetchone()
                
                if result:
                    return LobApplication(
                        lob_app_id=result[0],
                        application_name=result[1],
                        lob=result[2],
                        auto_resolve=result[3],
                        environment=result[4],
                        git_remote_url=result[5],
                        lookup_branch_pattern=result[6],
                        filter_pii=result[7],
                        created_ts=result[8].isoformat(),
                        updated_ts=result[9].isoformat(),
                        notification_dls=result[10],
                        app_info_actuator_url=result[11],
                        jira_projects_url=result[12],
                        app_dynamics_url=result[13]
                    )
                
                return None
                
        except psycopg2.Error as e:
            log.error(f"Failed to retrieve lob application with ID {lob_app_id}: {e}")
            raise

    def find_by_lob(self, lob: str) -> list[LobApplication]:
        """
        Retrieve all lob applications for a specific LOB.
        
        Args:
            lob (str): The LOB name to filter by
            
        Returns:
            list[LobApplication]: A list of lob applications for the specified LOB
        """
        log.info(f"Retrieving lob applications for lob: {lob}")
        
        try:
            with self._get_db_cursor() as cursor:
                select_query = """
                    SELECT lob_app_id, application_name, lob, auto_resolve, environment,
                           git_remote_url, lookup_branch_pattern, filter_pii,
                           created_ts, updated_ts, notification_dls, app_info_actuator_url,
                           jira_projects_url, app_dynamics_url
                    FROM lob_applications
                    WHERE lob = %s
                    ORDER BY application_name, environment;
                """
                
                cursor.execute(select_query, (lob,))
                results = cursor.fetchall()
                
                lob_applications = []
                for result in results:
                    lob_application = LobApplication(
                        lob_app_id=result[0],
                        application_name=result[1],
                        lob=result[2],
                        auto_resolve=result[3],
                        environment=result[4],
                        git_remote_url=result[5],
                        lookup_branch_pattern=result[6],
                        filter_pii=result[7],
                        created_ts=result[8].isoformat(),
                        updated_ts=result[9].isoformat(),
                        notification_dls=result[10],
                        app_info_actuator_url=result[11],
                        jira_projects_url=result[12],
                        app_dynamics_url=result[13]
                    )
                    lob_applications.append(lob_application)
                
                log.info(f"Found {len(lob_applications)} lob applications for lob: {lob}")
                return lob_applications
                
        except psycopg2.Error as e:
            log.error(f"Failed to retrieve lob applications for lob {lob}: {e}")
            raise

    def find_by_lob_application_and_environment(self, lob: str, application_name: str, environment: str) -> Optional[LobApplication]:
        """
        Retrieve a lob application by LOB, application name, and environment.
        
        Args:
            lob (str): The LOB name
            application_name (str): The application name
            environment (str): The environment
            
        Returns:
            Optional[LobApplication]: The lob application if found, None otherwise
        """
        log.info(f"Retrieving lob application for lob: {lob}, application: {application_name}, environment: {environment}")
        
        try:
            with self._get_db_cursor() as cursor:
                select_query = """
                    SELECT lob_app_id, application_name, lob, auto_resolve, environment,
                           git_remote_url, lookup_branch_pattern, filter_pii,
                           created_ts, updated_ts, notification_dls, app_info_actuator_url,
                           jira_projects_url, app_dynamics_url
                    FROM lob_applications
                    WHERE lob = %s AND application_name = %s AND environment = %s;
                """
                
                cursor.execute(select_query, (lob, application_name, environment))
                result = cursor.fetchone()
                
                if result:
                    lob_application = LobApplication(
                        lob_app_id=result[0],
                        application_name=result[1],
                        lob=result[2],
                        auto_resolve=result[3],
                        environment=result[4],
                        git_remote_url=result[5],
                        lookup_branch_pattern=result[6],
                        filter_pii=result[7],
                        created_ts=result[8].isoformat(),
                        updated_ts=result[9].isoformat(),
                        notification_dls=result[10],
                        app_info_actuator_url=result[11],
                        jira_projects_url=result[12],
                        app_dynamics_url=result[13]
                    )
                    log.info(f"Found lob application: {lob_application}")
                    return lob_application
                
                log.info(f"No lob application found for lob: {lob}, application: {application_name}, environment: {environment}")
                return None
                
        except psycopg2.Error as e:
            log.error(f"Failed to retrieve lob application for lob: {lob}, application: {application_name}, environment: {environment}: {e}")
            raise
    
    def close_connection_pool(self):
        """
        Close all connections in the pool.
        Should be called when the application shuts down.
        """
        if self._connection_pool:
            with self._pool_lock:
                if self._connection_pool:
                    self._connection_pool.closeall()
                    self._connection_pool = None
                    log.info("Database connection pool closed")
