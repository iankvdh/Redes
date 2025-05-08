from lib.parser import Parser
from lib.server import Server
from lib.logger import initialize_logger

def main():
    parser = Parser("Flags for server.")
    args = parser.parse_args_server()
    logger = initialize_logger(args.debug_level, "server")
    server = Server(args.host, args.port, args.protocol, args.storage, logger)
    server.start()

if __name__ == "__main__":
    main()
