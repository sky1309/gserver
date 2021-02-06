import json
import struct


class SocketProtocol:
    # 传输数据格式解析

    def __init__(self, fmt):
        # 由于可能㛮粘包的问题，所以在传输数据的过程中，需要在数据的头部加上一个表示
        self.struct = struct.Struct(fmt)

    def pack_data(self, data):
        """打包数据"""
        s = bytes(json.dumps(data))
        head = self.struct.pack(len(data))
        return head + s

    def unpack_data(self, data):
        """解析接收到的数据"""
        data_length = len(data)
        if data_length < self.struct.size:
            return b'', -1

        # 解析出head中标明后面的数据的长度
        valid_data_length, = self.struct.unpack_from(data, 0)
        offset = self.struct.size + valid_data_length
        # 如果数据还没有接受完毕，那么久先不处理
        if data_length < offset:
            return b'', -1

        return data[self.struct.size: offset], offset
