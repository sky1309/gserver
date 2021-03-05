import asyncore
import threading
from typing import Dict
from iface.imsghandler import IMsgHandler
from iface.iserver import IServer
from iface.iconnnection import ISocketConnection
from .common import log
from .connection import SocketConnection


class Server(IServer):

    def __init__(self, addr, backlog, msg_handler: IMsgHandler):
        super(Server, self).__init__(addr, backlog)

        # 操作conn的锁
        self._conns_lock = threading.Lock()
        # 操作conn_id的锁
        self._conn_id_lock = threading.Lock()

        # 管理的连接id
        self._global_client_id = 0
        # 所有的连接 map[int]ISocketConnection
        self._conns = dict()
        # 消息处理
        self._msg_handler = msg_handler

        # 是否已经关闭
        self._is_close = False

    def gen_conn_id(self):
        """生成client的id，id是递增的"""
        with self._conn_id_lock:
            self._global_client_id += 1
            d = self._global_client_id
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

    def handle_accepted(self, sock, addr):
        # 收到socket连接后创建一个连接对象
        cid = self.gen_conn_id()
        conn = SocketConnection(cid, self._msg_handler, sock)
        self.add_conn(conn)

    def serve_forever(self):
        log.info("serve start: {}".format(self.addr))
        self._msg_handler.start()
        try:
            asyncore.loop()
        except KeyboardInterrupt:
            self.serve_stop()

    def serve_stop(self):
        self._is_close = True
        # 关闭多线程的东西
        self._msg_handler.stop()
        log.info("serve stop: {}".format(self.addr))

