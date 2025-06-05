from huey import SqliteHuey
import time
import logging

from app.model.error_event import ErrorEvent

# Use SQLite as broker
huey_instance = SqliteHuey("tasksdb", filename="../tasks.db")
log = logging.getLogger(__name__)


# @huey_instance.task()
# def add(a: int, b: int):
#     log.info("Starting task to add numbers:", a, b)
#     for i in range(5):
#         log.info(f"Working... step {i+1}")
#         time.sleep(1)
#
#     log.info("Adding numbers:", a, b)
#     return a + b


@huey_instance.task()
def submit_error_event(error_event: ErrorEvent):
    """
    Task to submit an error event.

    Args:
        error_event (dict): The error event data to be processed.
    """
    log.info("Submitting error event:", error_event)
    # Simulate processing time
    time.sleep(2)
    for i in range(5):
        log.info(f"Working... step {i+1}")
        time.sleep(1)
    log.info("Error event submitted successfully")
    return error_event
