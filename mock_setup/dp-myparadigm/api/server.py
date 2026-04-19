"""
Dareplane server for the paradigm module.

This wraps the paradigm in a Dareplane-compatible TCP server that responds
to primary commands (PCOMMs) for remote control via dp-control-room.
"""

from dareplane_utils.default_server.server import DefaultServer
from fire import Fire

from myparadigm.paradigm import Paradigm
from myparadigm.utils.logging import logger


def run_server(
    ip: str = "localhost", port: int = 8084, log_level: str = "INFO"
) -> None:
    """
    Start the paradigm server.

    Parameters
    ----------
    port : int
        Port for the primary command TCP server.
    log_level : str
        Logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR").
    **kwargs
        Additional arguments passed to Paradigm.
    """
    logger.setLevel(log_level.upper())

    # Create the paradigm instance
    paradigm = Paradigm()

    # Define the primary commands (PCOMMs) that this module responds to
    pcomm_map = {
        "RUN": paradigm.run,
    }

    # Create and start the Dareplane server
    server = DefaultServer(
        ip=ip,
        port=port,
        pcommand_map=pcomm_map,
        name="dp-myparadigm",
    )

    # Run the server (blocking)
    server.init_server()
    server.start_listening()


if __name__ == "__main__":
    Fire(run_server)
