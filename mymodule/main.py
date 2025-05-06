# Just wrap the code with fire to also have a CLI
import time
from threading import Event, Thread

from fire import Fire

# The modules logger is used everywhere necessary. Note this logger will usually only have a NetworkHandler.
# If you want to log to the console, you need to add a StreamHandler to it.
from mymodule.utils.logging import logger


# We will link this function to the server later, so we want to return an int, a thread or a subprocess
# Int this exmaple I will use and int
def run_hello_world(n: int = 5, suffix: str = "") -> int:

    for i in range(n):
        logger.info(f"Hello World! {suffix}")

    return 0


def log_time() -> tuple[Thread, Event]:

    stop_event = Event()

    def _log_time():
        while not stop_event.is_set():
            logger.info(f"Time: {time.asctime()}")
            time.sleep(1)

    thread = Thread(target=_log_time)
    thread.start()

    return thread, stop_event


if __name__ == "__main__":
    Fire(run_hello_world)
