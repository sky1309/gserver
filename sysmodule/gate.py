from twisted.internet import reactor

from log import log
from module import module
from net import protocol, datapack, connmanager


class GateService(module.ModuleService):

    def handle_requests(self, *requests):
        for req in requests:
            self.call_handler("transmit", req)


def get_transmit_nodeid():
    # 获取转发一个转发的节点
    return 2


class GateModule(module.Module):
    """网关模块"""
    netfactory = None
    # config = {"port": 6666, "max_connection_num": 1000}
    transmit_node_func = None

    def on_init(self):
        self.netfactory = protocol.ServerFactory()
        self.netfactory.config = protocol.FactoryConfig(self.config["port"])

        # 断开连接回调
        if self.config.get("conn_lost_callback"):
            self.netfactory.conn_lost_callback = self.config["conn_lost_callback"]
        # 最大连接数
        max_connection_num = self.config.get("max_connection_num")
        if max_connection_num:
            self.netfactory.config.max_connection_num = int(max_connection_num)

        # *** 数据包参数处理
        # 单次包的最大大小
        # 消息头的长度
        # 大小端
        self.netfactory.datapack = datapack.DataPack()
        max_msg_len = self.config.get("max_msg_len")
        if max_msg_len:
            self.netfactory.datapack.max_msg_len = int(max_msg_len)
        head_len = self.config.get("head_len")
        if head_len:
            self.netfactory.datapack.set_head_len(head_len)
        little_endian = self.config.get("little_endian", False)
        if little_endian:
            self.netfactory.datapack.set_little_endian(little_endian)

        # 消息处理
        service = GateService("gate")
        service.set_module(self)
        # netfactory和rpc server共用一个service
        self.netfactory.service = service
        self.cluster.pb_server.set_service(self.netfactory.service)
        self._init_service()

        # 监听端口
        reactor.listenTCP(self.netfactory.config.port, self.netfactory)

    def _init_service(self):

        # 转发(转发客户端的数据到服务器)
        @self.netfactory.service.route("transmit")
        def transmit(request):
            nodeid = self.transmit_node_func() if self.transmit_node_func else get_transmit_nodeid()
            log.lgserver.debug(f"transmit, target: {nodeid}, request: {request}")
            self.cluster.call_node(nodeid, request.msg_id, request.conn.id, request.data)

        # 推送给指定的链接
        @self.netfactory.service.route("sendto_session")
        def sendto_session(caller, msg_id, data, *sessions):
            log.lgserver.debug(f"sendto_session, node: {caller.node_id}, msgid: {msg_id}, len: {len(data)}, {data}")
            self.netfactory.conn_manager.sendto_sessions(connmanager.Response(msg_id, data), sessions)

        # 广播给所有的玩家
        @self.netfactory.service.route("broadcast")
        def broadcast(caller, msg_id, data):
            log.lgserver.debug(f"broadcast, node: {caller.node_id}, msgid: {msg_id}, len: {len(data)}, {data}")
            self.netfactory.conn_manager.sendto_all(connmanager.Response(msg_id, data))
