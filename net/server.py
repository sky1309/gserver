import asyncore
import threading
from typing import Dict, Callable

from iface.imsghandler import IMsgHandler
from iface.iroute import IRoute
from iface.iserver import IServer
from iface.iconnnection import ISocketConnection
from util.common import log
from .connection import SocketConnection
from .protocol import default_socket_protocol


class Server(IServer):

    def __init__(self, addr, backlog, msg_handler: IMsgHandler):
        super(Server, self).__init__(addr, backlog)

        # 操作conn的锁
        self._conns_lock = threading.Lock()
        # 操作conn_id的锁
        self._conn_id_lock = threading.Lock()

        # 管理的连接id
        self._global_conn_id = 0
        # 所有的连接 map[int]ISocketConnection
        self._conns = dict()

        # 消息处理
        self._msg_handler = msg_handler

        # 是否已经关闭
        self._is_close = False

        # 创建、断开连接时的hook函数
        self._on_conn_start = None
        self._on_conn_close = None

        # 传输的数据协议
        self._protocol = default_socket_protocol()

    def gen_conn_id(self):
        """生成client的id，id是递增的"""
        with self._conn_id_lock:
            self._global_conn_id += 1
            d = self._global_conn_id
        return d

    def get_conns(self) -> Dict[int, ISocketConnection]:
        return self._conns

    def add_conn(self, conn: ISocketConnection):
        with self._conns_lock:
            self._conns[conn.get_cid()] = conn

    def remove_conn(self, cid):
        with self._conns_lock:
            # 这里 self.clients 里面的删除以后，WeakValueDictionary 里面的client会直接没掉
            self._conns.pop(cid, None)

    def add_route(self, msg_id: int, route: IRoute):
        """添加路由"""
        self._msg_handler.add_route(msg_id, route)

    def call_on_conn_start(self, conn: ISocketConnection):
        # 链接创建时
        if self._on_conn_start:
            self._on_conn_start(conn)

    def set_on_conn_start(self, func: Callable[[ISocketConnection], None]):
        self._on_conn_start = func

    def call_on_conn_close(self, conn: ISocketConnection):
        # 链接断开时
        if self._on_conn_close:
            self._on_conn_close(conn)

    def set_on_conn_close(self, func: Callable[[ISocketConnection], None]):
        self._on_conn_close = func

    def handle_accepted(self, sock, addr):
        # 收到socket连接后创建一个连接对象
        cid = self.gen_conn_id()
        conn = SocketConnection(self, cid, self._msg_handler, sock)
        conn.set_socket_protocol(self._protocol)

        self.add_conn(conn)
        # 调用链接创建时的函数
        self.call_on_conn_start(conn)

    def serve_forever(self):
        log.info("serve start: {}".format(self.addr))
        self._msg_handler.start()
        try:
            asyncore.loop(0.01)
        except KeyboardInterrupt:
            self.serve_stop()

    def serve_stop(self):
        self._is_close = True
        # 关闭多线程的东西
        self._msg_handler.stop()
        log.info("serve stop: {}".format(self.addr))

