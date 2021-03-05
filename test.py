from iface import IRequest
from net import server
from net.msghandler import MsgHandler
from net.route import BaseRoute


class Route(BaseRoute):
    def handle(self, request: IRequest):
        print('route handle', request)


if __name__ == '__main__':
    s = server.Server(("127.0.0.1", 8000), 5, MsgHandler())
    s.add_route(1, Route())
    s.serve_forever()
