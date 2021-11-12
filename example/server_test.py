import server
import globalobject

from util import timer
from net.connmanager import Request, Response

from cluster.pb import Root
from cluster.service import Service


# 断开连接的回调
server.start_netfactory(8000).conn_lost_callback = lambda d: print("offline callback.", d)


# 注册路由
@globalobject.netservice_handler(1)
def ping_view(request: Request):
    request.conn.send_response(Response(2, b'response body'))


# 测试的发送数据给所有的连接
def sendto_all():
    globalobject.netfactory.conn_manager.sendto_all(Response(1, b'pong!!!'))


# 定时循环
timer.add_loop_task(3, sendto_all, now=False)


service = Service("root_service")


@service.route(1)
def foo():
    print("service foo!!!")


if __name__ == '__main__':
    # 远程的服务器
    root = Root()
    root.set_service(service)
    root.start(8001)
    server.serve_forever()
