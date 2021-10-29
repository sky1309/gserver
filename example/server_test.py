import server

from net import msghandler
from net.connmanager import Request, Response

from util import timer


def ping_view(request: Request):
    request.conn.send_response(Response(2, b'response body'))


# 注册路由
msghandler.register_route(1, ping_view)

# 断开连接的回调
server.set_connection_lost(lambda d: print("offline callback.", d))


# 测试的发送数据给所有的连接
def sendto_all():
    server.factory.conn_manager.sendto_all(Response(1, b'pong!!!'))


# 定时循环
timer.add_loop_task(3, sendto_all, now=False)


if __name__ == '__main__':
    server.serve_forever(8000)
