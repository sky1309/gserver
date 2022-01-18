import json
import time

from twisted.internet import reactor

import server
from util import timer
from common import log
from net import protocol, msghandler

logic_nodes = (2, )


class MsgHandler(msghandler.JsonMsgHandler):
    def __init__(self):
        super(MsgHandler, self).__init__()

    def process_package(self, package):
        log.lgserver.debug(f"=== Receive data: {package}")
        parsed_data = json.loads(package.data.decode())

        # 转发数据到逻辑服务器（分布式的操作）
        # df = server.cluster.call_node(random.choice(logic_nodes), parsed_data["a"], parsed_data)

        # 直接给客户端发送数据
        # package.conn.write_message(b'process package...')
        self.dispatch(parsed_data["a"], package.conn, parsed_data)

    def dispatch(self, key, *args, **kwargs):
        conn = args[0]

        def _process():
            # 为了避险通一个连接同时在不同线程中执行，使用一下锁
            with conn.lock:
                super(MsgHandler, self).dispatch(key, *args, **kwargs)

        # 调用twisted的reactor线程池做数据的处理
        reactor.callInThread(_process)


netfactory = protocol.ServerFactory()
netfactory.config = protocol.FactoryConfig(8000)
# 断开连接的回调
netfactory.conn_lost_callback = lambda d: print("连接断开.", d)
netfactory.handler = MsgHandler()


@netfactory.handler.route_method(name="ping")
def ping_view(conn, data):
    conn.write(b"nihao" + str(data).encode())


# 测试的发送数据给所有的连接
def sendto_all():
    netfactory.conn_manager.sendto_all(b'hhhhhhhh' + str(time.time()).encode())


# 定时循环
timer.add_loop_task(2, sendto_all, now=False)

reactor.listenTCP(netfactory.config.port, netfactory)


if __name__ == '__main__':
    server.serve_forever()
