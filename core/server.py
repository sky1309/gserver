import bson
import weakref
import asyncore
import threading

from .common import log
from .protocol import SocketProtocol
from .connection import SocketServer


class Client:
    # 如果缓冲区的数据接收的太多，一直没处理，需要清理一下，别溢出了
    MAX_RECV_BUFFER_SIZE = 256 * 1024

    def __init__(self, handler, server, client_id=None):

        self._id = client_id or self.gen_client_id()

        self.socket_handler = handler
        self._server = server

        self.socket_handler.client = self
        # 客户端收到的数据缓冲区
        self._recv_buffer = bytearray()

        self._is_close = False

    @property
    def pk(self):
        return self._id

    @pk.setter
    def pk(self, value):
        self._id = value

    @property
    def server(self):
        return self._server

    @property
    def is_close(self):
        return self._is_close

    def register_client(self):
        # 注册进去
        self._server.register_client(self)

    def handle_read(self, data: bytearray):
        # 客户端处理数据，self.socket_handler发送火来的数据
        log.info("client {} 接收到handler发来的数据 {}".format(self._id, data))
        result_length = len(self._recv_buffer) + len(data)
        if result_length > self.MAX_RECV_BUFFER_SIZE:
            self.clear_recv_buffer()
            log.warning("数据超出最低限制 %d/%d" % (result_length, self.MAX_RECV_BUFFER_SIZE))
            return

        self._recv_buffer.extend(data)
        while self._recv_buffer:
            data, offset = self._server.protocol.split_data(data)

            # 数据没有完毕
            if offset < 0:
                break

            self._recv_buffer = self._recv_buffer[offset:]
            # 处理数据
            self.add_to_handle_queue(data)

    def handle_close(self):
        print("client close!")
        if self._is_close:
            return

        self._is_close = True
        self._server.remove_client(self)

    def send(self, data):
        byte_data = self._server.protocol.pack_data(data)
        self.socket_handler.send_data(byte_data)

    def add_to_handle_queue(self, data):
        """发送到处理线程"""
        pass
        # self._server.handle_thread.put(data)

    def clear_recv_buffer(self):
        self._recv_buffer.clear()

    @staticmethod
    def gen_client_id():
        return str(bson.ObjectId())


class Server:
    client_class = Client
    socket_server_class = SocketServer

    def __init__(self, addr, backlog, protocol=None):
        self.socket_server = self.socket_server_class(addr, backlog, self)

        self.client_operation_lock = threading.Lock()
        # 所有的连接 map[string]client
        self._clients = dict()
        # 已经登陆过的所有客户端
        self._register_clients = weakref.WeakValueDictionary()

        self._protocol = protocol or self.get_default_protocol_ins()

        # 多线处理
        # self.handle_thread = RequestHandleThread()
        # self.handle_thread.start()

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        self._protocol = value

    @staticmethod
    def get_default_protocol_ins():
        # 默认的数据处理协议，解决粘包什么的（右对齐，4字节，数据大小应该够用了）
        return SocketProtocol(">I")

    def new_client(self, handler):
        """有客户端连接上了，新建一个客户端，并存储
        """
        with self.client_operation_lock:
            client = self.client_class(handler, self)
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

    def serve_forever(self):
        log.info("serve start: {}".format(self.socket_server.addr))
        asyncore.loop()
