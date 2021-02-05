import bson


class Client:
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

    @staticmethod
    def gen_client_id():
        return str(bson.ObjectId())

    def get_id(self):
        return self._id

    def set_id(self, value):
        self._id = value
