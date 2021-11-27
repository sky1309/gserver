from twisted.internet import reactor
from util import timer

from cluster.service import Service

import server
from net.connmanager import Request, Response
from net import protocol, msghandler


netfactory = protocol.ServerFactory()

# 断开连接的回调
netfactory.conn_lost_callback = lambda d: print("offline callback.", d)
netfactory.service = msghandler.MsgHandler()


def ping_view(request: Request):
    request.conn.send_response(Response(2, b'response body'))


# 注册路由
netfactory.service.register_route(1, ping_view)


# 测试的发送数据给所有的连接
def sendto_all():
    netfactory.conn_manager.sendto_all(Response(1, b'pong!!!'))


# 定时循环
timer.add_loop_task(3, sendto_all, now=False)


service = Service("root_service")


@service.route(1)
def foo():
    print("service foo!!!")


reactor.listenTCP(8000, netfactory)


if __name__ == '__main__':
    server.serve_forever()
