from twisted.spread import pb
from twisted.internet import reactor


class Root(pb.Root):
    def __init__(self):
        # cluster.service.Service
        self._service = None

    def start(self, port):
        reactor.listenTCP(port, pb.PBServerFactory(self))

    def remote_ping(self):
        return "pong"

    def set_service(self, service):
        """设置消息处理"""
        self._service = service

    def remote_handle(self, nodeid, key, *args, **kwargs):
        """调用远程的服务"""
        return self._service.call_handler(key, *args, **kwargs)


class Remote:
    def __init__(self, host, port, name):
        self._host = host
        self._port = port
        self._name = name
        self._factory = None

    def connect_remote(self):
        self._factory = pb.PBClientFactory()
        reactor.connectTCP(self._host, self._port, self._factory)

    def call_remote_handler(self, nodeid, name, *args, **kwargs):
        """调用远程的处理函数"""
        root = self._factory.getRootObject()
        return root.addCallback(lambda d: d.callRemote("handle", nodeid, name, *args, **kwargs))
