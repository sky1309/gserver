import bson


class Client:
    # 如果缓冲区的数据接收的太多，一直没处理，需要清理一下，别溢出了
    MAX_RECV_BUFFER_SIZE = 256 * 1024

    def __init__(self, handler, server, client_id=None):

        self._id = client_id or self.gen_client_id()

        self.handler = handler
        self._server = server

        self.handler.client = self
        # 客户端收到的数据缓冲区
        self._recv_buffer = bytearray()

    def register_client(self):
        # 注册进去
        self._server.register_client(self)

    def handle_data(self, data: bytearray):
        # 客户端处理数据，self.handler发送火来的数据
        print("client {} 接收到handler发来的数据".format(self._id), data)
        if len(self._recv_buffer) + len(data) > self.MAX_RECV_BUFFER_SIZE:
            self.clear_recv_buffer()
            return

        self._recv_buffer.extend(data)
        while self._recv_buffer:
            data, offset = self._server.protocol.unpack_data(data)

            # 数据没有完毕
            if offset < 0:
                break

            # TODO 处理数据

            self._recv_buffer = self._recv_buffer[offset:]

    def clear_recv_buffer(self):
        self._recv_buffer.clear()

    @staticmethod
    def gen_client_id():
        return str(bson.ObjectId())

    @property
    def pk(self):
        return self._id

    @pk.setter
    def pk(self, value):
        self._id = value
