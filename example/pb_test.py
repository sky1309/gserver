from util import timer

import server
from cluster.service import Service
from cluster.cluster import cluster

s = Service("test_service")


@s.route("ping")
def ping():
    print("ping")
    return {
        "a": 1,
        "b": 2
    }


# 初始化节点数据
cluster.pb_server.set_service(s)


def foo():
    df = cluster.call_node(1, "ping")
    if df:
        df.addCallback(lambda d: print(d))


timer.add_loop_task(2, foo)

server.serve_forever()
