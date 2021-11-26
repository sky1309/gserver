from typing import Dict, Optional, List
from dataclasses import dataclass, field

from twisted.internet.defer import Deferred

from util import file
from config import globalconfig
from cluster.pb import Remote, Root


@dataclass
class Cluster:
    # 本地节点信息
    local_node_info: Optional[globalconfig.NodeInfo] = None
    # 本地监听的服务
    pb_server: Optional[Root] = None

    # 所有的节点数据
    remotes: Dict[int, Remote] = field(default_factory=dict)

    # 网关id列表(不是网关的服务可以通过遍历所有的网关，然后吧数据发送给所有的网关)
    gates: List[int] = field(default_factory=list)
    # 所有的服务器列表 [1, 2, 3]，元素是nodeid
    servers: List[int] = field(default_factory=list)

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
        data = file.load_json_file(globalconfig.config_path)

        # 本地节点
        self.local_node_info = globalconfig.NodeInfo.from_dict(data["nodes"][str(local_node_id)])

        # 能被发现的节点
        for _info in map(lambda d: globalconfig.NodeInfo.from_dict(data["nodes"][str(d)]), data["discovery_nodes"]):
            if _info.node_id == local_node_id:
                continue
            self.remotes[_info.node_id] = Remote(_info.host, _info.port, _info.name)

        # 所有的网关
        self.gates = list(map(int, data["gates"].keys()))

        # 网关转发选择发服务列表
        self.servers = data["servers"]

    def console_nodes(self):
        print(f"my node: {self.local_node_info.node_id}, cluster nodes: ", [i for i in self.remotes.keys()])

    def call_node(self, node_id, name, *args, **kwargs) -> Optional[Deferred]:
        if node_id not in self.remotes:
            return
        return self.remotes[node_id].call_remote_handler(self.local_node_info.node_id, name, *args, **kwargs)


cluster = Cluster()
