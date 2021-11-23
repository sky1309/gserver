import socket

from net.datapack import DataPack
from net.connmanager import Response


def main():
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.connect(("127.0.0.1", 8000))

    datapack = DataPack()
    data = datapack.pack_response(Response(1, b'abc'))
    ss.send(data)
    while True:
        revc = ss.recv(1024)
        if not revc:
            break
        print("receive data: ", revc)


if __name__ == '__main__':
    main()
