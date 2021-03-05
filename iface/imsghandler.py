import threading
from types import FunctionType
from typing import List
from abc import abstractmethod

from .iprotocol import IRequest, IResponse


class IMsgHandler:

    @abstractmethod
    def add_to_task_queue(self, *requests: IRequest):
        pass

    @abstractmethod
    def add_route(self, route_id: int, handler: FunctionType):
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
