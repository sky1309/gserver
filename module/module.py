from typing import Optional

from log import log
from cluster import cluster as pcluster


class Module:
    cluster: Optional[pcluster.Cluster] = None

    def __init__(self, name, cluster=None, config=None):
        # 名称
        self.name = name
        # 集群通讯
        self.cluster = cluster
        # 配置
        self.config = config

    def on_init(self):
        # 初始化完成
        pass

    def start(self):
        pass

    def stop(self):
        try:
            self.on_stop()
        except Exception as e:
            log.lgserver.error(f"module {self.name} stop error!!!, {e}")
        log.lgserver.debug(f"stop module {self.name}.")

    def on_stop(self):
        pass
