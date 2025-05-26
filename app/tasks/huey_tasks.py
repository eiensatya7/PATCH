from huey import SqliteHuey
import time
import logging

# Use SQLite as broker
huey_instance = SqliteHuey("tasksdb", filename="../tasks.db")
log = logging.getLogger(__name__)


@huey_instance.task()
def add(a: int, b: int):
    log.info("Starting task to add numbers:", a, b)
    for i in range(5):
        log.info(f"Working... step {i+1}")
        time.sleep(1)

    log.info("Adding numbers:", a, b)
    return a + b
