import asyncore
from abc import ABCMeta


class ISocketConnection(asyncore.dispatcher, metaclass=ABCMeta):
    # 管理单个链接的
    pass

