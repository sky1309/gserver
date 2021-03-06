# sample-game-server
tcp游戏echo服务器，客户端发送服务器指定格式的数据格式，服务器获取对应的协议号，走不同的逻辑函数


## Start

```python
#  Server
from iface import IRequest
from net import server
from iface.iconnnection import ISocketConnection

from net.msghandler import MsgHandler
from net.route import BaseRoute
from net.protocol import Response


class Route(BaseRoute):
    def handle(self, request: IRequest):
        print('route handle', request)
        request.get_conn().send_data(bytes(b"hello world!\n"))
        response = Response(1, bytes(b"response: z x c v b n m.\n"))
        request.get_conn().send_msg(response)


def on_start(conn: ISocketConnection):
    print("on start", conn)
    conn.send_data(bytes(b"conn on start\n"))


def on_close(conn: ISocketConnection):
    print("on close", conn)


if __name__ == '__main__':
    s = server.Server(("127.0.0.1", 8000), 5, MsgHandler())
    s.add_route(1, Route())
    s.set_on_conn_start(on_start)
    s.set_on_conn_close(on_close)
    s.serve_forever()


```

```python
# Client
import socket
import json
import struct

ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.connect(("127.0.0.1", 8000))
st = struct.Struct(">I")
d = json.dumps({"c": "hello_world", "d": {}}).encode()
ss.send(st.pack(len(d)) + st.pack(1) + d)
ss.recv(1024)
```