from abc import ABCMeta, abstractmethod
from .iconnnection import ISocketConnection


class IRequest(metaclass=ABCMeta):
    @abstractmethod
    def get_msg_id(self) -> int:
        pass

    @abstractmethod
    def get_d(self) -> bytearray:
        pass

    @abstractmethod
    def get_conn(self) -> ISocketConnection:
        pass

    @abstractmethod
    def set_conn(self, conn: ISocketConnection):
        pass


class IResponse(metaclass=ABCMeta):

    @abstractmethod
    def get_msg_id(self) -> int:
        pass

    @abstractmethod
    def get_d(self) -> bytearray:
        pass


class ISocketProtocol(metaclass=ABCMeta):

    @abstractmethod
    def pack(self, response: IResponse) -> bytearray:
        # 打包数据
        pass

    @abstractmethod
    def unpack(self, byte_data: bytearray) -> (IResponse, int):
        # 解包数据
        pass

    @abstractmethod
    def get_head_len(self) -> int:
        # 获取数据头的长度，粘包的问题
        pass
