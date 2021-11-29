import random

import server
from sysmodule import gate as sysmodulegate


#################
# 网关的2个作用
#   1. 处理客户端的连接，接受并解析，转发给逻辑服务器
#   2. 接受远程逻辑服务器的数据，并发给客户端
#################

def transmit_node_func():
    return random.choice([2])


def conn_lost(conn):
    nodeid = transmit_node_func()
    print(f"conn lost {nodeid}")
    server.cluster.call_node(nodeid, 2, conn.id)


gatemodule = sysmodulegate.GateModule("gate", server.cluster, config={"port": 1111, "conn_lost_callback": conn_lost})
gatemodule.transmit_node_func = transmit_node_func

# 注册模块
server.setup(
    gatemodule,
)

server.serve_forever()
