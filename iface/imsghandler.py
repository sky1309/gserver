import threading
from typing import List
from abc import abstractmethod

from .iprotocol import IRequest
from .iroute import IRoute


class IMsgHandler:

    @abstractmethod
    def add_to_task_queue(self, *requests: IRequest):
        pass

    @abstractmethod
    def add_route(self, msg_id: int, route: IRoute):
        pass

    @abstractmethod
    def get_max_worker(self) -> int:
        pass

    @abstractmethod
    def get_thread_pool(self) -> List[threading.Thread]:
        pass

    @abstractmethod
    def start(self):
        # 开启
        pass

    @abstractmethod
    def stop(self):
        # 关闭
        pass
