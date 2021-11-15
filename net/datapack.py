import struct

from config.globalconfig import NET_CONFIG

from .connmanager import Request, Response


class DataPack:
    # 传输数据格式解析

    def __init__(self, fmt=None, message_id_fmt=None):
        if fmt is None:
            fmt = NET_CONFIG.default_fmt
        if message_id_fmt is None:
            message_id_fmt = NET_CONFIG.default_message_id_fmt

        # 由于可能㛮粘包的问题，所以在传输数据的过程中，需要在数据的头部加上一个表示
        self.head_struct = struct.Struct(fmt)
        self.message_id_struct = struct.Struct(message_id_fmt)

    def pack(self, data: bytes) -> bytes:
        """打包数据"""
        return self.head_struct.pack(len(data)) + data

    def pack_response(self, response: Response):
        data = self.message_id_struct.pack(response.msg_id) + response.body
        return self.pack(data)

    def unpack(self, data: bytes) -> (Request, int):
        """解析接收到的数据"""
        data_length = len(data)
        head_length = self.get_head_len()
        # 数据没有接受完
        if data_length < head_length:
            return None, -1

        message_length, = self.head_struct.unpack_from(data, 0)

        # 本条数据的结束为止
        end_index = head_length + message_length
        # 如果数据还没有接受完毕，那么久先不处理
        if data_length < end_index:
            return None, -1

        message_id, = self.message_id_struct.unpack_from(data, head_length)
        return Request(message_id, data[head_length + self.message_id_struct.size: end_index]), end_index

    def get_head_len(self):
        """获取协议头的长度
        """
        return self.head_struct.size
