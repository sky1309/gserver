import asyncore
import threading


class SocketHandler(asyncore.dispatcher):
    # x kb
    # 一次最多接受的数据大小
    MAX_RECV_SIZE = 256 * 1024

    def __init__(self, sock=None, *args, **kwargs):
        super().__init__(sock, *args, **kwargs)
        self._client = None

        # 接受缓冲区
        self._recv_buffer = bytearray()
        # 写锁、发送缓冲区
        self._send_buffer = bytearray()
        self.write_lock = threading.Lock()

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    def handle_read(self):
        data = self.recv(self.MAX_RECV_SIZE)
        self._recv_buffer.extend(data)

        if self._client:
            self._client.handle_read(self._recv_buffer)

        # 清空接受缓冲区的数据
        self.clear_recv_buffer()

    def handle_write(self):
        if not self._send_buffer:
            return

        with self.write_lock:
            self.send(self._send_buffer)
            self.clear_recv_buffer()

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

    def clear_recv_buffer(self):
        self._recv_buffer.clear()


class SocketServer(asyncore.dispatcher):
    def __init__(self, addr, backlog, server=None):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind(addr)
        self.listen(backlog)

        # 总的服务对象
        self._server = server

    def handle_accepted(self, sock, addr):
        # 收到socket连接后创建一个连接对象
        handler = SocketHandler(sock)
        self._server.new_client(handler)

    def set_server(self, server):
        self._server = server
