# sample-game-server
tcp游戏echo服务器，客户端发送服务器指定格式的数据格式，服务器获取对应的协议号，走不同的逻辑函数


## Start

```python
# Server

from net import server

s = server.Server(("127.0.0.1", 8000), 5)


@s.route("hello_world")
def hello_world(request):
    request.client.send({
        "c": "hello world."
    })


if __name__ == '__main__':
    s.serve_forever()
```

```python
# Client

import socket
from net.server import Server

protocol = Server.get_default_protocol_ins()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(("127.0.0.1",8000))
s.send(protocol.pack_data({"c": "hello_world", "d": {}}))

print(s.recv(1024))
```
