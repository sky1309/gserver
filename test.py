from iface import IRequest
from net import server
from iface.iconnnection import ISocketConnection

from net.msghandler import MsgHandler
from net.route import BaseRoute


class Route(BaseRoute):
    def handle(self, request: IRequest):
        print('route handle', request)


def on_start(conn: ISocketConnection):
    print("on start", conn)


def on_close(conn: ISocketConnection):
    print("on close", conn)


if __name__ == '__main__':
    s = server.Server(("127.0.0.1", 8000), 5, MsgHandler())
    s.add_route(1, Route())
    s.set_on_conn_start(on_start)
    s.set_on_conn_close(on_close)
    s.serve_forever()
