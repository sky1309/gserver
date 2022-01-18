import time
import json
import socket
import threading

from net.datapack import DataPack

ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.connect(("127.0.0.1", 8000))

datapack = DataPack()
data = datapack.pack(json.dumps({
    "a": "ping",
    "d": {"hhhh": 1},
    "h": 1
}).encode())


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
