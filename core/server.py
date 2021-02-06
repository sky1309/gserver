import weakref
import asyncore
import threading

from .protocol import SocketProtocol
from .client import Client
from .connection import BaseSocketServer


class Server:
    client_cls = Client

    def __init__(self, addr, backlog, protocol=None):
        self.client_operation_lock = threading.Lock()
        self.socket_server = BaseSocketServer(addr, backlog, self)

        # 所有的连接 map[string]client
        self._clients = dict()
        # 已经登陆过的所有客户端
        self._register_clients = weakref.WeakValueDictionary()

        self._protocol = protocol or self.get_default_protocol_ins()

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        self._protocol = value

    @staticmethod
    def get_default_protocol_ins():
        return SocketProtocol(">I")

    def run(self):
        asyncore.loop(use_poll=True)

    def new_client(self, handler):
        """有客户端连接上了，新建一个客户端，并存储
        """
        with self.client_operation_lock:
            client = self.client_cls(handler, self)
            self._clients[client.pk] = client

    def remove_client(self, client):
        with self.client_operation_lock:
            # 这里 self.clients 里面的删除以后，WeakValueDictionary 里面的client会直接没掉
            self._clients.pop(client.pk, None)

    def register_client(self, client):
        with self.client_operation_lock:
            client_id = client.pk
            if client_id not in self._clients:
                return
            self._register_clients[client_id] = client
