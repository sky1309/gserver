from abc import ABCMeta, abstractmethod

from iface.iconnnection import ISocketConnection


class IClient(metaclass=ABCMeta):

    @abstractmethod
    def get_conn(self) -> ISocketConnection:
        pass

    @abstractmethod
    def set_conn(self, conn: ISocketConnection):
        pass
