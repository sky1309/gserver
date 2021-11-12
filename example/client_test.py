import socket
from twisted.internet import reactor

from cluster.pb import Remote
from net.datapack import DataPack
from net.connmanager import Response


def main():
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.connect(("127.0.0.1", 8000))

    datapack = DataPack()
    data = datapack.pack_response(Response(1, b'abc'))
    ss.send(data)

    while True:
        import time
        t = time.time()
        print(ss.recv(1024))
        print("use time:", time.time() - t)


def main_pb_client():

    r = Remote("gate")
    r.connect_remote("", 8001)
    r.call_remote_handler(1).addCallback(lambda d: print("response", d))

    reactor.run()


if __name__ == '__main__':
    main()
    # main_pb_client()
