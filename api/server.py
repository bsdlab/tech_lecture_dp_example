from dareplane_utils.default_server.server import DefaultServer
from fire import Fire
from mymodule.main import log_time, run_hello_world
from mymodule.utils.logging import logger


def main(port: int = 8080, ip: str = "127.0.0.1", loglevel: int = 10):
    logger.setLevel(loglevel)

    pcommand_map = {
        "HELLO": run_hello_world,  # here you would hook up the functionality of your module to the server
        "LOOP": log_time,
    }

    server = DefaultServer(
        port, ip=ip, pcommand_map=pcommand_map, name="mymodule_control_server"
    )

    # initialize to start the socket
    server.init_server()
    # start processing of the server
    logger.info(
        f"Server intialized, starting to listen for connections on: {ip=}, {port=}"
    )
    server.start_listening()

    return 0


if __name__ == "__main__":
    Fire(main)
