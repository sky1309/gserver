import random
from twisted.internet import reactor

from log import log

import server
from cluster import cluster, service
from net import protocol, msghandler
from net.connmanager import Response


#################
# 网关的2个作用
#   1. 处理客户端的连接，接受并解析，转发给逻辑服务器
#   2. 接受远程逻辑服务器的数据，并发给客户端
#################
port = 1111
logic_servers = [2, ]
gate_service = service.Service("gate_service")
cluster.cluster.pb_server.set_service(gate_service)


def rand_logic_node():
    return random.choice(logic_servers)


class GateMsgHandler(msghandler.MsgHandler):

    def handle_request(self, request):
        # 做一个转发
        # 随机选择一个逻辑服务器做数据的处理
        nodeid = rand_logic_node()
        log.lgserver.debug(f"gate transpond, target: {nodeid}, msgid: {request.msg_id}, data:{request.data}")
        print(cluster.cluster.remotes)
        df = cluster.cluster.call_node(2, request.msg_id, request.conn.id, request.data)
        # request.conn.send_response(Response(100, b'zhexnbucuo'))


# 全局的前端连接factory 435
netfactory = protocol.ServerFactory()
# 配置文件
netfactory.config = protocol.FactoryConfig(port)
# 消息处理
netfactory.msg_handler = GateMsgHandler()


# gate以外的服务可以调用这个，给指定的session发送数据
@gate_service.route("sendto_session")
def sendto_session(caller, sessionid, msg_id, data):
    print(f"sendto_session... {caller}")
    netfactory.conn_manager.sendto_sessions(Response(msg_id, data), [sessionid])


@gate_service.route("broadcast")
def broadcast(caller, msg_id, data):
    print(f"broadcast... {caller}")
    netfactory.conn_manager.sendto_all(Response(msg_id, data))


# 启动网关
reactor.listenTCP(port, netfactory)
server.serve_forever()
