from twisted.internet import reactor

import globalobject
from net.protocol import ServerFactory


def start_netfactory(port, factory=None):
    """启动网关服务"""
    if factory is None:
        factory = ServerFactory()

    # 设置全局的factory对象
    globalobject.netfactory = factory

    print(f"[netfactory] listen tcp address: http://0.0.0.0:{port}")
    reactor.listenTCP(port, factory)
    return factory


def serve_forever():
    """启动服务器"""
    reactor.run()
