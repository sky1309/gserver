import argparse
from twisted.internet import reactor

import globalobject
from net.protocol import ServerFactory
from cluster import cluster

parser = argparse.ArgumentParser()
# 节点id（rpc）
parser.add_argument("-nodeid", required=True, dest="nodeid", type=int)
# ....
# 系统的参数
sys_args = parser.parse_args()


def _init_server():
    # 初始化集群数据
    cluster.cluster.init_cluster(sys_args.nodeid)


# 初始化集群数据
_init_server()


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
