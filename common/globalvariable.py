import argparse

#################
# 全局的变量
#################

# 系统的参数处理
parser = argparse.ArgumentParser()
# 节点id（rpc）
parser.add_argument("-nodeid", dest="nodeid", type=int, default=1)
# 日志等级
parser.add_argument("-dl", dest="debuglevel", type=str, default="INFO")

# ....
sysargs, _ = parser.parse_known_args()
