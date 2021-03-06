import asyncore
from typing import Dict, Callable
from abc import ABCMeta, abstractmethod

from .iconnnection import ISocketConnection
from .iroute import IRoute


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
    def call_on_conn_start(self, conn: ISocketConnection):
        # 链接创建时
        pass

    @abstractmethod
    def set_on_conn_start(self, func: Callable[[ISocketConnection], None]):
        pass

    @abstractmethod
    def call_on_conn_close(self, conn: ISocketConnection):
        # 链接断开时
        pass

    @abstractmethod
    def set_on_conn_close(self, func: Callable[[ISocketConnection], None]):
        pass

    @abstractmethod
    def remove_conn(self, cid: int):
        pass

    @abstractmethod
    def handle_conn_close(self, conn: ISocketConnection):
        # server 的某个conn断开后的调用
        pass

    @abstractmethod
    def add_route(self, msg_id: int, route: IRoute):
        pass

    @abstractmethod
    def serve_forever(self):
        # run server
        pass

    @abstractmethod
    def serve_stop(self):
        # close server
        pass
