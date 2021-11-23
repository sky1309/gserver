import json
from typing import Dict, Optional, List
from dataclasses import dataclass, field

from dataclasses_json import DataClassJsonMixin
from twisted.internet.defer import Deferred

from config import globalconfig
from cluster.pb import Remote, Root


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


@dataclass
class Cluster:
    # 本地节点信息
    local_node_info: Optional[NodeInfo] = None
    # 本地监听的服务
    pb_server: Optional[Root] = None

    # 所有的节点数据
    remotes: Dict[int, Remote] = field(default_factory=dict)

    # 网关id列表(不是网关的服务可以通过遍历所有的网关，然后吧数据发送给所有的网关)
    gates: List[int] = field(default_factory=list)

    def init_cluster(self, node_id):
        # 读取配置文件
        self._read_config(node_id)
        # 启动本地的
        self._start_local_node()
        # 连接到远端
        self._connect_remote()

    def _start_local_node(self):
        self.pb_server = Root()
        self.pb_server.start(self.local_node_info.port)

    def _connect_remote(self):
        self.console_nodes()
        for remote in self.remotes.values():
            remote.connect_remote()

    def _read_config(self, local_node_id: int):
        # 读取配置文件
        with open(globalconfig.config_path, "r") as f:
            data = json.load(f)

        for _info in map(lambda d: NodeInfo.from_dict(d), data["nodes"]):
            if _info.node_id == local_node_id:
                self.local_node_info = _info
            else:
                self.remotes[_info.node_id] = Remote(_info.host, _info.port, _info.name)

        # 所有的网关
        for gate in data["gates"]:
            self.gates.append(gate["node_id"])

    def console_nodes(self):
        print(f"my node: {self.local_node_info.node_id}, cluster nodes: ", [i for i in self.remotes.keys()])

    def call_node(self, node_id, name, *args, **kwargs) -> Optional[Deferred]:
        if node_id not in self.remotes:
            return
        return self.remotes[node_id].call_remote_handler(self.local_node_info.node_id, name, *args, **kwargs)


cluster = Cluster()
