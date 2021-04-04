from typing import Dict
from abc import abstractmethod

from .iconnnection import ISocketConnection


class IConnectionOperator:

    @abstractmethod
    def get_conns(self) -> Dict[int, ISocketConnection]:
        pass

    @abstractmethod
    def start(self):
        """启动tcp连接管理服务"""
        pass
