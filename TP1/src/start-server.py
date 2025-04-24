from lib.parser import Parser
from lib.server import Server

def main():
    
    parser = Parser("Flags for server.")
    args = parser.parse_args_server()

    verbose = args.verbose and not args.quiet
    if verbose:
        print("Verbose mode is enabled.")
    quiet = args.quiet and not args.verbose
    if quiet:
        print("Quiet mode is enabled.")

    server = Server(args.host, args.port, args.protocol, args.storage)

    try:
        server.start()
    except KeyboardInterrupt:
        print("Keyboard Interrup error. Server shutting down.")
        # server.close() ? 

if __name__ == "__main__":
    main()
