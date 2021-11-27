from typing import Union
from dataclasses import dataclass

from twisted.spread import pb
from twisted.internet import reactor

from log import log
from util import timer


def client_reconnect(connector):
    """客户端重连"""
    log.lgserver.debug(f"{connector} reconnecting...")
    connector.connect()


@dataclass
class CallerInfo:
    """Remote调用方的信息"""
    # 远程节点id
    node_id: int
    # 消息id || service的路由id
    msg_id: Union[str, int]


class ClusterPBServerFactory(pb.PBServerFactory):
    """集群rcp服务端"""
    def clientConnectionMade(self, protocol):
        """当有一个连接连接时"""
        pass


class ClusterPBClientFactory(pb.PBClientFactory):
    """集群rcp客户端"""
    # 重连的时间间隔
    reconnect_interval = 2

    def clientConnectionFailed(self, connector, reason):
        """客户端连接服务器失败后，尝试重新连接"""
        super(ClusterPBClientFactory, self).clientConnectionFailed(connector, reason)
        # 延迟重连
        timer.add_later_task(self.reconnect_interval, client_reconnect, connector)

    def clientConnectionLost(self, connector, reason, reconnecting=1):
        """连接端断开了，尝试重连"""
        super(ClusterPBClientFactory, self).clientConnectionLost(connector, reason, reconnecting)
        # 延迟重连
        timer.add_later_task(self.reconnect_interval, client_reconnect, connector)


class Root(pb.Root):
    def __init__(self):
        # cluster.service.Service
        self._service = None

    def start(self, port):
        reactor.listenTCP(port, ClusterPBServerFactory(self))

    def set_service(self, service):
        """设置消息处理"""
        self._service = service

    def remote_ping(self):
        return "pong"

    def remote_handle(self, nodeid, key, *args, **kwargs):
        """调用远程的服务"""
        caller = CallerInfo(nodeid, key)
        return self._service.call_handler(key, caller, *args, **kwargs)


class Remote:
    def __init__(self, host, port, name):
        self._host = host
        self._port = port
        self._name = name
        self._factory = None

    def connect_remote(self):
        self._factory = ClusterPBClientFactory()
        # 连接远端的时候必须增加延时操作
        # 加了失败重连和断线重连后，可以不用延迟了...
        # reactor.connectTCP(self._host, self._port, self._factory)
        timer.add_later_task(1, reactor.connectTCP, self._host, self._port, self._factory)

    def call_remote_handler(self, nodeid, name, *args, **kwargs):
        """调用远程的处理函数
        参数:
          - nodeid: int 调用人的节点id
        """
        root = self._factory.getRootObject()
        return root.addCallback(lambda d: d.callRemote("handle", nodeid, name, *args, **kwargs))
