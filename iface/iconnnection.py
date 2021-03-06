import asyncore
from abc import ABCMeta, abstractmethod

from .iprotocol import ISocketProtocol
from .iresponse import IResponse


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

    @abstractmethod
    def send_data(self, byte_data: bytes):
        pass

    @abstractmethod
    def send_msg(self, response: IResponse):
        pass

    @abstractmethod
    def get_socket_protocol(self) -> ISocketProtocol:
        pass

    @abstractmethod
    def set_socket_protocol(self, protocol: ISocketProtocol):
        pass


class IRequest(metaclass=ABCMeta):
    @abstractmethod
    def get_msg_id(self) -> int:
        pass

    @abstractmethod
    def get_d(self) -> bytes:
        pass

    @abstractmethod
    def get_conn(self) -> ISocketConnection:
        pass

    @abstractmethod
    def set_conn(self, conn: ISocketConnection):
        pass
