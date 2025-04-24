from lib.parser import Parser
from lib.client import Client

def main():

    parser = Parser("Flags for upload.")
    args = parser.parse_args_upload()

    verbose = args.verbose and not args.quiet
    if verbose:
        print("Verbose mode is enabled.")
    quiet = args.quiet and not args.verbose
    if quiet:
        print("Quiet mode is enabled.")

    # args.port args.host args.name args.protocol
    client = Client(args.host, args.port, args.protocol) 
    
    try:
        client.upload_file(args.src, args.name)
    except Exception as e:
        print(f"Error uploading file: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
