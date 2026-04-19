"""
Minimal socket connection to mimic telnet.
This script is used as an auxiliary tool to test the TCP server of the
Dareplane modules.
"""

import socket
import sys
import select
from fire import Fire


def telpy(host: str, port: int):
    """
    Connect to host:port and send stdin input to socket until interrupted.

    Parameters
    ----------
    host : str
        Target IP address or hostname.
    port : int
        Target port number.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            sock.setblocking(False)

            # Read welcome message
            try:
                banner = sock.recv(1024).decode("utf-8")
                print(banner, end="")
            except BlockingIOError:
                pass

            print(f"Connected to {host}:{port}", file=sys.stderr)

            try:
                while True:
                    # Check for input from stdin or socket
                    ready_to_read, _, _ = select.select([sys.stdin, sock], [], [], 0.1)

                    # Read from stdin and send to socket
                    if sys.stdin in ready_to_read:
                        line = sys.stdin.readline()
                        if not line:  # EOF
                            break
                        # Ensure proper line ending for socket protocol (CRLF)
                        line = line.rstrip("\n\r") + "\r\n"
                        sock.sendall(line.encode("utf-8"))

                    # Read from socket and print to stdout
                    if sock in ready_to_read:
                        try:
                            data = sock.recv(1024)
                            if not data:  # Connection closed
                                print("\nRemote connection closed", file=sys.stderr)
                                break
                            print(data.decode("utf-8"), end="")
                        except BlockingIOError:
                            pass

            except KeyboardInterrupt:
                print("\nInterrupted by user", file=sys.stderr)
            except BrokenPipeError:
                print("\nRemote connection closed", file=sys.stderr)

    except ConnectionRefusedError:
        print(f"Connection refused to {host}:{port}", file=sys.stderr)
        sys.exit(1)
    except socket.gaierror as e:
        print(f"Invalid host: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    Fire(telpy)
