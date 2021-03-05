import threading

from iface.iconnnection import ISocketConnection
from .protocol import default_socket_protocol


class SocketConnection(ISocketConnection):
    # x kb
    # 一次最多接受的数据大小
    MAX_RECV_SIZE = 256 * 1024

    def __init__(self, sock=None, *args, **kwargs):
        super().__init__(sock, *args, **kwargs)

        # 接受缓冲区
        self._recv_buffer = bytearray()
        self._send_buffer = bytearray()
        # 写锁、发送缓冲区
        self.read_lock = threading.Lock()
        self.write_lock = threading.Lock()

        # protocol
        self.protocol = default_socket_protocol()

    def handle_read(self):
        data = self.recv(self.MAX_RECV_SIZE)
        with self.read_lock:
            self._recv_buffer.extend(data)

        request, offset = self.protocol.unpack(self._recv_buffer)
        if offset < 0 or not request:
            return

        # 读取数据以后
        with self.write_lock:
            self._recv_buffer = self._recv_buffer[offset:]

        print(":request", request)

    def handle_write(self):
        if not self._send_buffer:
            return

        with self.write_lock:
            self.send(self._send_buffer)
            self._send_buffer.clear()

    def writable(self):
        return len(self._send_buffer) > 0

    def send_data(self, data: bytearray):
        """发送数据"""
        with self.write_lock:
            self._send_buffer.extend(data)

    def handle_close(self):
        # 客户端关闭连接的时候会调用
        # 不知道为啥，这里会被调用2次，所以这里要处理一下，不能走两次回到哦
        if self._client:
            self._client.handle_close()
        self.close()
