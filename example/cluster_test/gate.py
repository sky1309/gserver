import random

import server
from sysmodule import gate as sysmodulegate

#################
# 网关的2个作用
#   1. 处理客户端的连接，接受并解析，转发给逻辑服务器
#   2. 接受远程逻辑服务器的数据，并发给客户端
#################

gatemodule = sysmodulegate.GateModule("gate", server.cluster, config={"port": 1111})
gatemodule.transmit_node_func = lambda: random.choice([2])

# 注册模块
server.setup(
    gatemodule,
)

server.serve_forever()
