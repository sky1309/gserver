import time
import json
import socket
import threading

from net.datapack import DataPack
from net.connmanager import Response

ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.connect(("127.0.0.1", 1111))

datapack = DataPack()
data = datapack.pack_response(Response(1, json.dumps({"userid": "abcde", "password": "123456"}).encode()))


def target():
    while True:
        time.sleep(1)
        ss.send(data)


t = threading.Thread(target=target)
t.setDaemon(True)
t.start()

ss.send(data)
while True:
    revc = ss.recv(1024)
    if not revc:
        break
    print("receive data: ", revc)
