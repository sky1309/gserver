from twisted.internet import reactor

# 初始化配置数据
from cluster import cluster


# * 初始化集群数据 -nodeid=1
cluster.cluster.init_cluster(cluster.sys_args.nodeid)


def serve_forever():
    """启动服务器"""
    reactor.run()
