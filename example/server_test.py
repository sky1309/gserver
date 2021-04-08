from iface import IRequest
from net import server
from iface.iconnnection import ISocketConnection

from net.msghandler import MsgHandler
from net.route import BaseRoute
from net.protocol import Response
from net.connoperator import ConnectionOperator


class Route(BaseRoute):
    def handle(self, request: IRequest):
        print('route handle', request)
        request.get_conn().send_data(bytes(b"hello world!\n"))
        response = Response(1, bytes(b"response: z x c v b n m.\n"))
        request.get_conn().send_msg(response)


def on_start(conn: ISocketConnection):
    print("on start", conn)
    conn.send_data(bytes(b"conn on start\n"))


def on_close(conn: ISocketConnection):
    print("on close", conn)


if __name__ == '__main__':
    s = server.Server(("127.0.0.1", 8000), 5, MsgHandler())
    # 添加路由
    s.add_route(1, Route())

    # 建立连接、关闭连接走的回调函数
    s.set_on_conn_start(on_start)
    s.set_on_conn_close(on_close)

    # 添加连接操作器，ConnectionOperator 内部可以实现广播，推送这些东西
    s.set_connoperator(ConnectionOperator(s))

    s.serve_forever()
