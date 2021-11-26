import os
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin

# 配置文件路径项目启动目录下面 WORKSPACE/config/cluster.json
cluster_config_path = os.path.join(os.getcwd(), "config/cluster.json")


@dataclass
class NodeInfo(DataClassJsonMixin):
    # 节点id
    node_id: int
    # 节点名称
    name: str
    # 地址
    host: str
    # 监听的端口，远程调用
    port: int
