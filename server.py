import argparse

from twisted.internet import reactor

from cluster import cluster as pcluster
from module import modulemgr


# 系统的参数处理
parser = argparse.ArgumentParser()
# 节点id（rpc）
parser.add_argument("-nodeid", required=True, dest="nodeid", type=int)
# ....
sys_args = parser.parse_args()


# * 初始化集群数据 -nodeid=1
cluster = pcluster.Cluster()
cluster.init_cluster(sys_args.nodeid)


def setup(*modules):
    # 服务配置模块
    for module in modules:
        modulemgr.setup(module)


def serve_forever():
    """启动服务器"""
    # 初始化模块
    modulemgr.init()
    # 启动模块
    modulemgr.start()

    # ** 启动twisted主循环
    reactor.run()

    # 停止所有模块
    modulemgr.stop()
