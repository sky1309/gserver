import threading
import weakref

from .client import Client
from .connection import BaseSocketServer


class Server:
    client_cls = Client

    def __init__(self, addr, backlog):
        self.client_operation_lock = threading.Lock()
        self.socket_server = BaseSocketServer(addr, backlog, self)

        # 请求处理的函数
        self._request_handler = None

        # 所有的连接 map[string]client
        self._clients = dict()
        # 已经登陆过的所有客户端
        self._keyed_clients = weakref.WeakValueDictionary()

    def register_client(self, client):
        client_id = client.get_id()
        if client_id in self._clients:
            self._keyed_clients[client_id] = client

    def new_client(self, handler):
        with self.client_operation_lock:
            client = self.client_cls(handler, self)
            self._clients[client.get_id()] = client

    def remove_client(self, client):
        with self.client_operation_lock:
            # 这里 self.clients 里面的删除以后，WeakValueDictionary 里面的client会直接没掉
            self._clients.pop(client.get_id(), None)

    @property
    def request_handler(self):
        return self._request_handler

    @request_handler.setter
    def request_handler(self, value):
        assert callable(value), "无效的函数类型"
        self._request_handler = value
