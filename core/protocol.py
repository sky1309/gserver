import json
import struct

from marshmallow import fields, schema, utils as marshmallow_utils


class SocketProtocol:
    # 传输数据格式解析

    def __init__(self, fmt):
        # 由于可能㛮粘包的问题，所以在传输数据的过程中，需要在数据的头部加上一个表示
        self.struct = struct.Struct(fmt)

    def pack_data(self, data):
        """打包数据"""
        s = self.dumps(data).encode()
        head = self.struct.pack(len(data))
        return head + s

    def unpack_data(self, bytes_data):
        data = self.loads(bytes_data)
        return data

    def split_data(self, bytes_data):
        """解析接收到的数据"""
        data_length = len(bytes_data)
        if data_length < self.struct.size:
            return None, -1

        # 解析出head中标明后面的数据的长度
        valid_data_length, = self.struct.unpack_from(bytes_data, 0)
        offset = self.struct.size + valid_data_length
        # 如果数据还没有接受完毕，那么久先不处理
        if data_length < offset:
            return None, -1

        return bytes_data[self.struct.size: offset], offset

    @staticmethod
    def loads(bytes_data):
        return json.loads(bytes_data.decode())

    @staticmethod
    def dumps(data):
        return json.dumps(data)


class ProtocolStruct(schema.Schema):
    # 数据传输的结构

    # command 指令
    c = fields.String(required=True, validate=lambda k: len(k) > 0)
    # data 数据
    d = fields.Mapping()

    class Meta:
        unknown = marshmallow_utils.EXCLUDE


class ProtocolResponseStruct(schema.Schema):
    # command 指令
    c = fields.String(required=True, validate=lambda k: len(k) > 0)
    # data 数据
    d = fields.Mapping()
    # 状态码
    s = fields.Integer()


class Request:
    def __init__(self, client, c, d, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)
        self.cmd = c
        self.params = d
        self.client = client


class Response:
    def __init__(self, c, d, s=0):
        self.c = c
        self.d = d or dict()
        self.s = s
