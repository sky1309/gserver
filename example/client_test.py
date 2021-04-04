import socket

from net.protocol import Response, SocketProtocol


def main():
    protocol = SocketProtocol()
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.connect(("127.0.0.1", 8000))

    ss.send(protocol.pack(Response(1, b"send data...")))
    ss.recv(1024)


if __name__ == '__main__':
    main()
