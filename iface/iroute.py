from abc import ABCMeta, abstractmethod

from .iconnnection import IRequest


class IRoute(metaclass=ABCMeta):

    @abstractmethod
    def pre_handle(self, request: IRequest):
        # 进入视图函数之前
        pass

    @abstractmethod
    def handle(self, request: IRequest):
        # 逻辑函数
        pass

    @abstractmethod
    def post_handle(self, request: IRequest):
        # 进入视图函数时候
        pass

    def do(self, request: IRequest):
        self.pre_handle(request)
        self.handle(request)
        self.post_handle(request)
