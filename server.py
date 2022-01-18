
from twisted.internet import reactor

from common import globalvariable
from cluster import cluster as pcluster
from module import modulemgr


# * 初始化集群数据 -nodeid=1
cluster = pcluster.Cluster()
cluster.init_cluster(globalvariable.sysargs.nodeid)


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
