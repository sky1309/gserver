from twisted.internet import reactor

import server
from cluster import cluster
from cluster import service
from net import protocol, msghandler
from net.connmanager import Response


gate_service = service.Service("gate_service")
cluster.cluster.pb_server.set_service(gate_service)


class GateMsgHanlder(msghandler.MsgHandler):
    def handle_request(self, request):
        # 做一个转发
        print("ping_view")
        df = cluster.cluster.call_node(2, request.msg_id, server.sys_args.nodeid, request.conn.id, request.data)
        df.addCallback(lambda d: print("logic foo callback", d))
        print("finish ping view")
        request.conn.send_response(Response(1, b'nmd'))


# 全局的前端连接factory
netfactory = protocol.ServerFactory()
# 消息处理
netfactory.msg_handler = GateMsgHanlder()


# gate以外的服务可以调用这个，给指定的session发送数据
@gate_service.route("sendto_session")
def sendto_session(sessionid, msg_id, data):
    print("sendto_session...")
    netfactory.conn_manager.sendto_sessions(Response(msg_id, data), [sessionid])


@gate_service.route("broadcast")
def broadcast_handler(msg_id, data):
    netfactory.conn_manager.sendto_all(Response(msg_id, data))


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


# 启动网关
reactor.listenTCP(8000, netfactory)
# 启动服务
server.serve_forever()
