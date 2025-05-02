from lib.parser import Parser
from lib.client import Client
from lib.logger import initialize_logger

def main():
    parser = Parser("Flags for upload.")
    args = parser.parse_args_upload()
    logger = initialize_logger(args.debug_level, "upload")
    # args.port args.host args.name args.protocol
    client = Client(args.host, args.port, args.protocol, logger) 
    client.upload_file(args.src, args.name)


if __name__ == "__main__":
    main()
