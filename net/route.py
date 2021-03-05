from iface import IRequest
from iface.iroute import IRoute


class BaseRoute(IRoute):
    def pre_handle(self, request: IRequest):
        pass

    def handle(self, request: IRequest):
        pass

    def post_handle(self, request: IRequest):
        pass
