from socket import *
import argparse
from lib.client import Client


def main():
    parser = argparse.ArgumentParser(description="Upload files to server.")

    parser.add_argument("-h", "--help", help="show this help message and exit")
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
        "-H", "--host", type=str, default="127.0.0.1", help="server IP address"
    )
    parser.add_argument("-p", "--port", type=int, default=12000, help="server port")
    parser.add_argument("-s", "--src", default="", help="source file path")
    parser.add_argument("-n", "--name", type=str, default="", help="file name")
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

    # args.port args.host args.name args.protocol
    client = Client(args.host, args.port, args.protocol) 
    client.upload_file(args.src, args.name)
    client.close()


if __name__ == "__main__":
    main()


# Definimos el nombre del Server y su port
serverName = "localhost"  # Acá debería estar el Hostname o IP del servidor
serverPort = 12000

# Creamos nuestro Socket Cliente
clientSocket = socket(AF_INET, SOCK_DGRAM)
# AF_INET significa usar IPv4
# SOCK_DGRAM significa usar UDP

# Definimos el mensaje a enviar por el server
message = input("Input the text to convert to uppercase: ")
# Enviamos el mensaje - Usamos encode() para convertir el mensaje en bytes
clientSocket.sendto(message.encode(), (serverName, serverPort))

# Eschuchamos la respuesta con buffer size 2048, cliente se bloquea esperando el msg
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
# decode() convierte el mensaje en Texto
print(modifiedMessage.decode())
# Cerramos el socket
clientSocket.close()
