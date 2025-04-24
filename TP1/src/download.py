from lib.parser import Parser
from lib.client import Client

def main():

    parser = Parser("Flags for download.")
    args = parser.parse_args_download()

    verbose = args.verbose and not args.quiet
    if verbose:
        print("Verbose mode is enabled.")
    quiet = args.quiet and not args.verbose
    if quiet:
        print("Quiet mode is enabled.")

    client = Client(args.host, args.port, args.protocol)

    try: 
        client.download_file(args.dst, args.name)
    except Exception as e:
        print(f"Error downloading file: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
