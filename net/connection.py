import threading

from util.common import log

from iface import IRequest, IResponse, IServer, ISocketProtocol
from iface.iconnnection import ISocketConnection
from iface.imsghandler import IMsgHandler

from .protocol import default_socket_protocol


class SocketConnection(ISocketConnection):
    # x kb
    # 一次最多接受的数据大小
    MAX_RECV_SIZE = 256 * 1024
    # 一次handle_read最多尝试的次数
    MAX_HANDLE_TRY = 10
    # 如果同时玩家的请求书很多的时候，先扔到处理队列中去
    MAX_REQUEST_LIST_SIZE = 100

    def __init__(self, server: IServer, cid, msg_handler: IMsgHandler, sock=None, *args, **kwargs):
        super().__init__(sock, *args, **kwargs)

        # 链接id
        self._cid = cid
        self._server = server

        # 接受缓冲区
        self._recv_buffer = bytes()
        self._send_buffer = bytes()
        # 写锁、发送缓冲区
        self.read_lock = threading.Lock()
        self.write_lock = threading.Lock()

        # protocol
        self._protocol = default_socket_protocol()

        self.c = 0
        self._msg_handler = msg_handler

        # 是否已经关闭
        self._is_close = False

    def _read_data(self):
        try:
            data = self.recv(self.MAX_RECV_SIZE)
            with self.read_lock:
                self._recv_buffer += data
        except BlockingIOError:
            # print("[conn read data err] ", e)
            pass

    def handle_read(self):
        """读取数据的时候"""
        log.info("[conn {}] handle read...".format(self._cid))
        requests = list()

        try_count = 0
        while True:
            # 没有需要接受接受的数据了，跳过
            self._read_data()
            if not self.get_recv_buffer_size() or try_count > self.MAX_HANDLE_TRY:
                print("[conn {}] conn handle read loop.".format(self._cid))
                break

            request: IRequest
            request, offset = self._protocol.unpack(self._recv_buffer)
            if offset < 0 or not request:
                try_count += 1
                return

            # 读取数据以后
            with self.write_lock:
                self._recv_buffer = self._recv_buffer[offset:]

            self.c += 1
            request.set_conn(self)
            requests.append(request)
            # 如果 requests 中量很大了，先扔到处理的队列中去
            if len(requests) >= self.MAX_REQUEST_LIST_SIZE:
                print("[conn {}] requests is full: size=", len(requests))
                self._msg_handler.add_to_task_queue(*requests)
                requests = list()

        # 添加到处理队列中去
        if requests:
            self._msg_handler.add_to_task_queue(*requests)

    def handle_write(self):
        if not self._send_buffer:
            return

        # 计算字节数
        send = self.send(self._send_buffer)
        with self.write_lock:
            self._send_buffer = self._send_buffer[send:]

    def writable(self):
        return len(self._send_buffer) > 0

    def send_data(self, data: bytes):
        """发送数据"""
        with self.write_lock:
            self._send_buffer += data

    def send_msg(self, response: IResponse):
        """发送response格式的数据"""
        data = self.get_socket_protocol().pack(response)
        self.send_data(data)

    def handle_close(self):
        if self._is_close:
            print("[conn {}] close error, conn is closed.".format(self._cid))
            return
        # 客户端关闭连接的时候会调用
        # 不知道为啥，这里会被调用2次，所以这里要处理一下，不能走两次回到哦
        self._is_close = True
        self.close()
        # 关闭的处理函数
        self._server.call_on_conn_close(self)
        print("[conn {}] close success".format(self._cid))

    def get_recv_buffer_size(self):
        return len(self._recv_buffer)

    def get_send_buffer_size(self):
        return len(self._send_buffer)

    def get_cid(self) -> int:
        return self._cid

    def set_cid(self, cid: int):
        self._cid = cid

    def get_socket_protocol(self) -> ISocketProtocol:
        return self._protocol

    def set_socket_protocol(self, protocol: ISocketProtocol):
        self._protocol = protocol
