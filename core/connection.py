import asyncore


class BaseSocketHandler(asyncore.dispatcher):
    # x kb
    # 一次最多接受的数据大小
    MAX_RECV_SIZE = 128 * 1024

    def __init__(self, sock=None, *args, **kwargs):
        super().__init__(sock, *args, **kwargs)
        self._client = None

        # 接受缓冲区
        self._recv_buffer = bytearray()

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    def handle_read(self):
        self._handle_read()
        if self._client:
            self._client.handle_data(self._recv_buffer)

        # 清空接受缓冲区的数据
        self.clear_recv_buffer()

    def _handle_read(self):
        data = self.recv(self.MAX_RECV_SIZE)
        self._recv_buffer.append(data)

    def clear_recv_buffer(self):
        self._recv_buffer.clear()


class BaseSocketServer(asyncore.dispatcher):
    def __init__(self, addr, backlog, server=None):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind(addr)
        self.listen(backlog)

        # 总的服务器
        self._server = server

    def handle_accepted(self, sock, addr):
        handler = BaseSocketHandler(sock)
        self._server.new_client(handler)

    def set_server(self, server):
        self._server = server
