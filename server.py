import argparse

from twisted.internet import reactor

# 初始化配置数据
from cluster import cluster


# 系统的参数处理
parser = argparse.ArgumentParser()
# 节点id（rpc）
parser.add_argument("-nodeid", required=True, dest="nodeid", type=int)
# ....
sys_args = parser.parse_args()


# * 初始化集群数据 -nodeid=1
cluster.cluster.init_cluster(sys_args.nodeid)


def serve_forever():
    """启动服务器"""
    reactor.run()
