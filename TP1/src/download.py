from lib.parser import Parser
from lib.client import Client
from lib.logger import initialize_logger

def main():

    parser = Parser("Flags for download.")
    args = parser.parse_args_download()
    logger = initialize_logger(args.debug_level, "download")
    client = Client(args.host, args.port, args.protocol, logger)
    client.download_file(args.dst, args.name)

if __name__ == "__main__":
    main()
