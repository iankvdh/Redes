import time
from lib.parser import Parser
from lib.client import Client
from lib.logger import initialize_logger

def main():
    parser = Parser("Flags for upload.")
    args = parser.parse_args_upload()
    logger = initialize_logger(args.debug_level, "upload")
    client = Client(args.host, args.port, args.protocol, logger) 

    start_time = time.time()
    client.upload_file(args.src, args.name)
    end_time = time.time()

    elapsed = end_time - start_time
    print(f"Upload completed in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()
