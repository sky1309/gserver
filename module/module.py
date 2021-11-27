from typing import Optional

from log import log
from cluster import cluster as pcluster


class Module:
    cluster: Optional[pcluster.Cluster] = None

    def __init__(self, cluster=None):
        self.cluster = cluster
        self.name = ""

    def start(self):
        self.on_start()

    def on_start(self):
        pass

    def stop(self):
        try:
            self.on_stop()
        except Exception as e:
            log.lgserver.error(f"module {self.name} stop error!!!, {e}")
        log.lgserver.debug(f"stop module {self.name}.")

    def on_stop(self):
        pass
