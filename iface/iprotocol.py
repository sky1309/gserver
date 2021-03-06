from abc import ABCMeta, abstractmethod

from .iresponse import IResponse


class ISocketProtocol(metaclass=ABCMeta):

    @abstractmethod
    def pack(self, response: IResponse) -> bytes:
        # 打包数据
        pass

    @abstractmethod
    def unpack(self, byte_data: bytes) -> (IResponse, int):
        # 解包数据
        pass

    @abstractmethod
    def get_head_len(self) -> int:
        # 获取数据头的长度，粘包的问题
        pass
