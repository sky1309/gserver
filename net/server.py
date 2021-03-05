import asyncore
import threading

from iface.iserver import IServer
from iface.iconnnection import ISocketConnection
from .common import log
from .connection import SocketConnection
from .client import Client


class Server(IServer):

    def __init__(self, addr, backlog):
        super(Server, self).__init__(addr, backlog)

        # 操作client的锁
        self._client_lock = threading.Lock()
        # 操作client_id的锁
        self._client_id_lock = threading.Lock()

        # TODO 管理的连接id
        self._client_id = 0
        # 所有的连接 map[string]client
        self._clients = dict()

    def gen_client_id(self):
        """生成client的id，id是递增的"""
        with self._client_id_lock:
            self._client_id += 1
            d = self._client_id
        return d

    def new_client(self, conn: ISocketConnection):
        cid = self.gen_client_id()
        with self._client_lock:
            self._clients[cid] = Client(cid, conn)

    def handle_accepted(self, sock, addr):
        # 收到socket连接后创建一个连接对象
        conn = SocketConnection(sock)
        self.new_client(conn)

    def remove_client(self, client):
        with self._client_lock:
            # 这里 self.clients 里面的删除以后，WeakValueDictionary 里面的client会直接没掉
            self._clients.pop(client.cid, None)

    def serve_forever(self):
        log.info("serve start: {}".format(self.addr))

        asyncore.loop(0.01, use_poll=True)
