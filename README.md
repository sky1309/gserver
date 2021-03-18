# simple-game-server
tcp游戏服务器，客户端发送服务器指定格式的数据格式，服务端解析出协议号，分发到不同的路由中
最近看了golang实现的轻量级tcp服务器 [```zinx```](https://github.com/aceld/zinx)，学习了他实现的实现思想，做了个python的实现版本。。。

## Protocol(协议)
```
  3 parts
    - 4 byte msg length
    - 4 byte msg id
    - msg body

-------------------------------------------------------------------------
  4 byte msg length       4 byte msg id(route id)           msg
     [][][][]                 [][][][]                  [][][]....[][][]
-------------------------------------------------------------------------
```

## Quick Start

### Install
    git clone https://github.com/prillc/simple-game-server.git

    cd simple-game-server
    
    pipenv sync

### Usage
```python
# Server
from iface import IRequest
from iface.iconnnection import ISocketConnection

from net import server
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
# Test Python Client
import socket

from net.protocol import Response, SocketProtocol

protocol = SocketProtocol()
ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.connect(("127.0.0.1", 8000))

ss.send(protocol.pack(Response(1, b"send data...")))
ss.recv(1024)

```
