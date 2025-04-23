import argparse
import os
from lib.server import Server

def main():
    parser = argparse.ArgumentParser(description="Starts server.")

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="increase output verbosity",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="decrease output verbosity",
    )
    parser.add_argument(
        "-H", "--host", type=str, default="localhost", help="host server IP address"
    )
    parser.add_argument("-p", "--port", type=int, default=8080, help="port server port")
    parser.add_argument("-s", "--storage", default=os.getcwd() + "/storage", help="storage dir path")
    parser.add_argument(
        "-r",
        "--protocol",
        type=str,
        choices=["sw", "sr"],
        default="sw",
        help="error recovery protocol",
    )  # stop and wait= sw, selective repeat= sr

    args = parser.parse_args()

    verbose = args.verbose and not args.quiet
    if verbose:
        print("Verbose mode is enabled.")
    quiet = args.quiet and not args.verbose
    if quiet:
        print("Quiet mode is enabled.")

    server = Server(args.host, args.port, args.protocol, args.storage)
    server.start()

if __name__ == "__main__":
    main()
