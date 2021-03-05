import asyncore
from abc import ABCMeta, abstractmethod


class ISocketConnection(asyncore.dispatcher, metaclass=ABCMeta):
    # 管理单个链接的

    @abstractmethod
    def get_recv_buffer_size(self):
        pass

    @abstractmethod
    def get_send_buffer_size(self):
        pass

    @abstractmethod
    def get_cid(self) -> int:
        pass

    @abstractmethod
    def set_cid(self, cid: int):
        pass
