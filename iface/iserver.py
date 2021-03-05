import asyncore
from typing import Dict
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
    def gen_conn_id(self) -> int:
        pass

    @abstractmethod
    def get_conns(self) -> Dict[int, ISocketConnection]:
        pass

    @abstractmethod
    def add_conn(self, conn: ISocketConnection):
        pass

    @abstractmethod
    def remove_conn(self, cid: int):
        pass

    @abstractmethod
    def serve_forever(self):
        # run server
        pass

    @abstractmethod
    def serve_stop(self):
        # close server
        pass
