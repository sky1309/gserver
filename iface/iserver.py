import asyncore
from abc import ABCMeta, abstractmethod

from .iconnnection import ISocketConnection


class IServer(asyncore.dispatcher, metaclass=ABCMeta):
    # 监听端口的socket服务
    def __init__(self, addr, backlog):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind(addr)
        self.listen(backlog)

    @abstractmethod
    def gen_client_id(self) -> int:
        pass

    @abstractmethod
    def new_client(self, conn: ISocketConnection):
        pass

    @abstractmethod
    def remove_client(self, cid: int):
        pass

    @abstractmethod
    def serve_forever(self):
        pass
