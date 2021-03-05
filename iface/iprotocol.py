from abc import ABCMeta, abstractmethod


class IRequest(metaclass=ABCMeta):
    @abstractmethod
    def get_msg_id(self) -> int:
        pass

    @abstractmethod
    def get_d(self) -> bytearray:
        pass

    @abstractmethod
    def get_client(self):
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
