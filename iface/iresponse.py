from abc import ABCMeta, abstractmethod


class IResponse(metaclass=ABCMeta):

    @abstractmethod
    def get_msg_id(self) -> int:
        pass

    @abstractmethod
    def get_d(self) -> bytes:
        pass
