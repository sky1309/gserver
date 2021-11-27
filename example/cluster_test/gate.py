from twisted.internet import reactor

from log import log

import server
from cluster import service
from net import protocol
from net.connmanager import Response


#################
# 网关的2个作用
#   1. 处理客户端的连接，接受并解析，转发给逻辑服务器
#   2. 接受远程逻辑服务器的数据，并发给客户端
#################
port = 1111


class GateService(service.Service):
    def handle_requests(self, *requests):
        for req in requests:
            self.call_handler("transmit", req)


gate_service = GateService("gate_service")

# 全局的前端连接factory 435
netfactory = protocol.ServerFactory()
# 配置文件
netfactory.config = protocol.FactoryConfig(port)
# 消息处理
netfactory.service = gate_service
# 设置集群rpc服务，目前是和gate的net共用一个
server.cluster.pb_server.set_service(gate_service)


@gate_service.route("transmit")
def transmit(request):
    server.cluster.call_node(2, request.msg_id, request.conn.id, request.data)


# gate以外的服务可以调用这个，给指定的session发送数据
@gate_service.route("sendto_session")
def sendto_sessions(caller, msg_id, data, *sessions):
    log.lgserver.debug(f"broadcast, callnode: {caller.node_id}, msgid: {msg_id}, len: {len(data)}")
    netfactory.conn_manager.sendto_sessions(Response(msg_id, data), sessions)


@gate_service.route("broadcast")
def broadcast(caller, msg_id, data):
    log.lgserver.debug(f"broadcast, callnode: {caller.node_id}, msgid: {msg_id}, len: {len(data)}")
    netfactory.conn_manager.sendto_all(Response(msg_id, data))


# 启动网关
reactor.listenTCP(port, netfactory)
server.serve_forever()
