"""
Dareplane server for the paradigm module.

This wraps the paradigm in a Dareplane-compatible TCP server that responds
to primary commands (PCOMMs) for remote control via dp-control-room.
"""

from dareplane_utils.default_server.server import DefaultServer
from fire import Fire

from myparadigm.paradigm import Paradigm


def run_paradigm(port: int = 8084, **kwargs) -> None:
    """
    Start the paradigm server.

    Parameters
    ----------
    port : int
        Port for the primary command TCP server.
    **kwargs
        Additional arguments passed to Paradigm.
    """
    # Create the paradigm instance
    paradigm = Paradigm(**kwargs)

    # Define the primary commands (PCOMMs) that this module responds to
    pcomm_map = {
        "RUN": paradigm.run,
        "STOP": paradigm.stop,
    }

    # Create and start the Dareplane server
    server = DefaultServer(
        port=port,
        pcomm_map=pcomm_map,
        name="dp-myparadigm",
    )

    # Run the server (blocking)
    server.run()


if __name__ == "__main__":
    Fire(run_paradigm)
