from twisted.internet import reactor

import server
from cluster import cluster
from cluster import service
from net import protocol
from net.connmanager import Response, Request


gate_service = service.Service("gate_service")
cluster.cluster.pb_server.set_service(gate_service)

# 全局的前端连接factory
netfactory = protocol.ServerFactory()


def broadcast_handler(msg_id, data):
    netfactory.conn_manager.sendto_all(Response(msg_id, data))


gate_service.register_handler("broadcast", broadcast_handler)


def net_handler(name):
    """注册基础网络的路由
    eg:
      @register_net_factory_handler(1)
      def foo(a, b):
        pass
    """

    def process(func):
        netfactory.msg_handler.register_route(name, func)

    return process


# 注册路由
@net_handler(1)
def ping_view(request: Request):
    print("ping_view")
    df = cluster.cluster.call_node(2, "foo", request.data)
    df.addCallback(lambda d: print("logic foo callback", d))
    print("finish ping view")
    request.conn.send_response(Response(1, b'nmd'))


# 启动网关
reactor.listenTCP(8000, netfactory)
# 启动服务
server.serve_forever()
