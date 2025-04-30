from lib.parser import Parser
from lib.client import Client

def main():

    parser = Parser("Flags for download.")
    args = parser.parse_args_download()

    client = Client(args.host, args.port, args.protocol)

    try: 
        client.download_file(args.dst, args.name)
    except Exception as e:
        print(f"Error downloading file: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
