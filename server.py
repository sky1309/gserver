from twisted.internet import reactor

from net.protocol import ServerFactory


factory = ServerFactory()


def set_connection_lost(callback):
    """连接断开的使用的回调函数（一般用于玩家离线后的逻辑处理）
    """
    factory.do_conn_lost = callback


def serve_forever(port):
    print(f"Listen tcp address: http://0.0.0.0:{port}")
    reactor.listenTCP(port, factory)
    reactor.run()
