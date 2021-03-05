from abc import ABCMeta, abstractmethod


class IClient(metaclass=ABCMeta):
    # 如果缓冲区的数据接收的太多，一直没处理，需要清理一下，别溢出了
    MAX_RECV_BUFFER_SIZE = 1024 * 1024

    @abstractmethod
    def get_cid(self) -> int:
        pass

    @abstractmethod
    def set_cid(self, cid: int):
        pass
