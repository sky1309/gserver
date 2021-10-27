# simple-game-server
tcp游戏服务器，客户端发送服务器指定格式的数据格式，服务端解析出协议号，分发到不同的路由中
最近看了golang实现的轻量级tcp服务器 [```zinx```](https://github.com/aceld/zinx)，学习了他实现的实现思想，做了个python的实现版本。。。

## Protocol(协议)
```
  3 parts
    - 4 byte msg length
 
    - msg body

-------------------------------------------------------------------------
  4 byte msg length       2 byte msg id(route id)  + msg
     [][][][]                 [][][]....[][][]
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
import server

from net import msghandler
from net.connmanager import Request, Response


def ping_view(request: Request):
    request.conn.send_response(Response(2, b'response body'))


msghandler.register_route(1, ping_view)


if __name__ == '__main__':
    server.serve_forever(8000)

```

```python
# Test Python Client
import socket

from net.datapack import DataPack
from net.connmanager import Response


def main():
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.connect(("127.0.0.1", 8000))

    datapack = DataPack()
    data = datapack.pack_response(Response(1, b'abc'))
    ss.send(data)
    ss.recv(1024)


if __name__ == '__main__':
    main()

```
