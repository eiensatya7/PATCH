import logging
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from typing import Optional
import os
import threading

from app.model.error_event import ErrorEvent

log = logging.getLogger(__name__)


class ErrorEventDao:
    """
    Data Access Object for ErrorEvent entities.
    Handles database connections and CRUD operations for error events.
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
        
        log.info("ErrorEventDao initialized")
    
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
    
    def save_error_event(self, error_event: ErrorEvent) -> ErrorEvent:
        """
        Save a new error event to the database.
        
        Args:
            error_event (ErrorEvent): The error event object to save
            
        Returns:
            ErrorEvent: The saved error event object
            
        Raises:
            psycopg2.Error: If database operation fails
        """
        log.info(f"Saving error event: {error_event}")
        
        try:
            with self._get_db_cursor() as cursor:
                # INSERT query matching the error_events table schema
                insert_query = """
                    INSERT INTO error_events (
                        lob_app_id,
                        event_state,
                        correlation_id,
                        span_id,
                        stacktrace,
                        origin_method,
                        occurrence_count,
                        error_timestamp,
                        origin_line_number,
                        origin_class
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING event_id, created_ts, updated_ts;
                """
                
                # Execute with actual error_event attributes
                cursor.execute(insert_query, (
                    error_event.lob_app_id,
                    error_event.event_state,
                    error_event.correlation_id,
                    error_event.span_id,
                    error_event.stacktrace,
                    error_event.origin_method,
                    error_event.occurrence_count,
                    error_event.error_timestamp,
                    error_event.origin_line_number,
                    error_event.origin_class
                ))
                
                # Get the returned values (ID and timestamps)
                result = cursor.fetchone()
                if result:
                    error_event.event_id = result[0]
                    error_event.created_ts = result[1].isoformat()
                    error_event.updated_ts = result[2].isoformat()
                    log.info(f"Error event saved successfully with ID: {error_event.event_id}")
                
            return error_event
            
        except psycopg2.Error as e:
            log.error(f"Failed to save error event: {e}")
            raise
    
    def find_by_id(self, event_id: int) -> Optional[ErrorEvent]:
        """
        Retrieve an error event by its ID.
        
        Args:
            event_id (int): The ID of the error event to retrieve
            
        Returns:
            Optional[ErrorEvent]: The error event if found, None otherwise
        """
        try:
            with self._get_db_cursor() as cursor:
                select_query = """
                    SELECT event_id, lob_app_id, event_state, correlation_id, span_id,
                           stacktrace, origin_method, resolution, pull_request_url,
                           confidence, user_resolution_acceptance, occurrence_count,
                           created_ts, updated_ts, error_timestamp, user_feedback,
                           origin_line_number, origin_class, source_branch, affected_jira_ids
                    FROM error_events
                    WHERE event_id = %s;
                """
                
                cursor.execute(select_query, (event_id,))
                result = cursor.fetchone()
                
                if result:
                    return ErrorEvent(
                        event_id=result[0],
                        lob_app_id=result[1],
                        event_state=result[2],
                        correlation_id=result[3],
                        span_id=result[4],
                        stacktrace=result[5],
                        origin_method=result[6],
                        resolution=result[7],
                        pull_request_url=result[8],
                        confidence=result[9],
                        user_resolution_acceptance=result[10],
                        occurrence_count=result[11],
                        created_ts=result[12].isoformat(),
                        updated_ts=result[13].isoformat(),
                        error_timestamp=result[14].isoformat(),
                        user_feedback=result[15],
                        origin_line_number=result[16],
                        origin_class=result[17],
                        source_branch=result[18],
                        affected_jira_ids=result[19],
                        # Set required fields with empty values since they're not stored in DB
                        lob="",
                        application_name="",
                        environment=""
                    )
                
                return None
                
        except psycopg2.Error as e:
            log.error(f"Failed to retrieve error event with ID {event_id}: {e}")
            raise

    def find_by_lob(self, lob: str) -> list[ErrorEvent]:
        """
        Retrieve all error events for a specific LOB by joining with lob_applications.
        
        Args:
            lob (str): The LOB name to filter by
            
        Returns:
            list[ErrorEvent]: A list of error events for the specified LOB
        """
        log.info(f"Retrieving error events for lob: {lob}")
        
        try:
            with self._get_db_cursor() as cursor:
                select_query = """
                    SELECT ee.event_id, ee.lob_app_id, ee.event_state, ee.correlation_id, 
                           ee.span_id, ee.stacktrace, ee.origin_method, ee.resolution,
                           ee.pull_request_url, ee.confidence, ee.user_resolution_acceptance,
                           ee.occurrence_count, ee.created_ts, ee.updated_ts, ee.error_timestamp,
                           ee.user_feedback, ee.origin_line_number, ee.origin_class,
                           ee.source_branch, ee.affected_jira_ids,
                           la.lob, la.application_name, la.environment
                    FROM error_events ee
                    JOIN lob_applications la ON ee.lob_app_id = la.lob_app_id
                    WHERE la.lob = %s
                    ORDER BY ee.created_ts DESC;
                """
                
                cursor.execute(select_query, (lob,))
                results = cursor.fetchall()
                
                error_events = []
                for result in results:
                    error_event = ErrorEvent(
                        event_id=result[0],
                        lob_app_id=result[1],
                        event_state=result[2],
                        correlation_id=result[3],
                        span_id=result[4],
                        stacktrace=result[5],
                        origin_method=result[6],
                        resolution=result[7],
                        pull_request_url=result[8],
                        confidence=result[9],
                        user_resolution_acceptance=result[10],
                        occurrence_count=result[11],
                        created_ts=result[12].isoformat(),
                        updated_ts=result[13].isoformat(),
                        error_timestamp=result[14].isoformat(),
                        user_feedback=result[15],
                        origin_line_number=result[16],
                        origin_class=result[17],
                        source_branch=result[18],
                        affected_jira_ids=result[19],
                        lob=result[20],
                        application_name=result[21],
                        environment=result[22]
                    )
                    error_events.append(error_event)
                
                log.info(f"Found {len(error_events)} error events for lob: {lob}")
                return error_events
                
        except psycopg2.Error as e:
            log.error(f"Failed to retrieve error events for lob {lob}: {e}")
            raise

    def update_event_state(self, event_id: int, new_state: str) -> None:
        """
        Update the state of an error event.
        
        Args:
            event_id (int): The ID of the error event to update
            new_state (str): The new state to set
            
        Raises:
            ValueError: If no error event found with the given ID
            psycopg2.Error: If database operation fails
        """
        log.info(f"Updating error event {event_id} state to: {new_state}")
        
        try:
            with self._get_db_cursor() as cursor:
                update_query = """
                    UPDATE error_events 
                    SET event_state = %s, updated_ts = now()
                    WHERE event_id = %s;
                """
                
                cursor.execute(update_query, (new_state, event_id))
                rows_affected = cursor.rowcount
                
                if rows_affected > 0:
                    log.info(f"Successfully updated error event {event_id} state to {new_state}")
                else:
                    log.error(f"No error event found with ID {event_id}")
                    raise ValueError(f"No error event found with ID {event_id}")
                
        except psycopg2.Error as e:
            log.error(f"Failed to update error event {event_id} state: {e}")
            raise

    def update_error_resolution(self, event_id: int, resolution: str, confidence: float, 
                               pull_request_url: str, event_state: str) -> None:
        """
        Update error event with resolution details.
        
        Args:
            event_id (int): The ID of the error event to update
            resolution (str): The resolution description
            confidence (float): The confidence level of the resolution
            pull_request_url (str): URL of the pull request containing the fix
            event_state (str): The new state of the error event
            
        Raises:
            ValueError: If no error event found with the given ID
            psycopg2.Error: If database operation fails
        """
        log.info(f"Updating error event {event_id} with resolution")
        
        try:
            with self._get_db_cursor() as cursor:
                update_query = """
                    UPDATE error_events 
                    SET resolution = %s, 
                        confidence = %s, 
                        pull_request_url = %s, 
                        event_state = %s, 
                        updated_ts = now()
                    WHERE event_id = %s;
                """
                
                cursor.execute(update_query, (resolution, confidence, pull_request_url, 
                                            event_state, event_id))
                rows_affected = cursor.rowcount
                
                if rows_affected > 0:
                    log.info(f"Successfully updated error event {event_id} with resolution")
                else:
                    log.error(f"No error event found with ID {event_id}")
                    raise ValueError(f"No error event found with ID {event_id}")
                
        except psycopg2.Error as e:
            log.error(f"Failed to update error event {event_id} with resolution: {e}")
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
