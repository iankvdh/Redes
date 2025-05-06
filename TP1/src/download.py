import time
from lib.parser import Parser
from lib.client import Client
from lib.logger import initialize_logger

def main():
    parser = Parser("Flags for download.")
    args = parser.parse_args_download()
    logger = initialize_logger(args.debug_level, "download")
    client = Client(args.host, args.port, args.protocol, logger)

    start_time = time.time()
    client.download_file(args.dst, args.name)
    end_time = time.time()

    elapsed = end_time - start_time
    print(f"Download completed in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()
