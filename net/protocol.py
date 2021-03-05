import struct
from dataclasses import dataclass

from dataclasses_json import dataclass_json
from marshmallow import fields, schema, utils as marshmallow_utils

from iface.iconnnection import ISocketConnection
from iface.iprotocol import IRequest, IResponse


@dataclass_json
@dataclass
class Request(IRequest):
    msg_id: int
    d: bytearray
    conn: ISocketConnection = None

    def get_msg_id(self) -> int:
        return self.msg_id

    def get_d(self) -> bytearray:
        return self.d

    def get_conn(self) -> ISocketConnection:
        return self.conn

    def set_conn(self, conn: ISocketConnection):
        self.conn = conn


@dataclass_json
@dataclass
class Response(IResponse):
    msg_id: int
    d: bytearray

    def get_msg_id(self) -> int:
        return self.msg_id

    def get_d(self) -> bytearray:
        return self.d


class SocketProtocol:
    # 传输数据格式解析

    MAX_ONCE_DATA_SIZE = 256 * 1024

    DEFAULT_FMT = ">I"
    DEFAULT_MSG_ID_FMT = ">I"

    def __init__(self, fmt=DEFAULT_FMT, msg_id_fmt=DEFAULT_MSG_ID_FMT):
        # 由于可能㛮粘包的问题，所以在传输数据的过程中，需要在数据的头部加上一个表示
        self.struct = struct.Struct(fmt)
        # msg id 的打包
        self.msg_id_struct = struct.Struct(msg_id_fmt)

    def pack(self, response: Response):
        """打包数据"""
        msg_len = self.struct.pack(len(response.d))
        return msg_len + self.msg_id_struct.pack(response.msg_id) + response.d

    def unpack(self, bytes_data) -> (Request, int):
        """解析接收到的数据"""
        data_length = len(bytes_data)
        head_length = self.get_head_len()
        # 数据没有接受完
        if data_length < head_length:
            return None, -1

        # 解析出head中标明后面的数据的长度
        msg_length, = self.struct.unpack_from(bytes_data, 0)
        # 消息id
        msg_id, = self.msg_id_struct.unpack_from(bytes_data, self.struct.size)

        # 本条数据的结束为止
        end_index = head_length + msg_length
        # 如果数据还没有接受完毕，那么久先不处理
        if data_length < end_index:
            return None, -1

        return Request(msg_id, bytes_data[head_length:end_index]), end_index

    def get_head_len(self):
        """获取协议头的长度
        """
        return self.struct.size + self.msg_id_struct.size


class ProtocolMsg(schema.Schema):
    # 数据传输的结构

    # command 指令 协议id
    # msg_id = fields.Integer(required=True)
    # data 数据
    d = fields.Mapping(required=True)

    class Meta:
        unknown = marshmallow_utils.EXCLUDE


def default_socket_protocol():
    """默认情况下的协议数据结构
       part1    part2     part3
    [][][][] [][][][]   [][][][][]
    含义:
      part1: msg数据的长度
      part2: 协议号（接口）
      part3: msg的数据，长度为part1 4个字节的的值
    """
    return SocketProtocol()


class ProtocolResponseStruct(schema.Schema):
    # command 指令
    c = fields.String(required=True, validate=lambda k: len(k) > 0)
    # data 数据
    d = fields.Mapping()
    # 状态码
    s = fields.Integer()

