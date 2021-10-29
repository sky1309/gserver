import socket

from net.datapack import DataPack
from net.connmanager import Response


def main():
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.connect(("127.0.0.1", 8000))

    datapack = DataPack()
    data = datapack.pack_response(Response(1, b'abc'))
    for i in range(100):
        ss.send(data)
    import time
    time.sleep(2)
    print(ss.recv(1024))


if __name__ == '__main__':
    main()
