import struct
from dataclasses import dataclass

from dataclasses_json import dataclass_json

from iface.iconnnection import ISocketConnection
from iface import IResponse, IRequest


@dataclass_json
@dataclass
class Request(IRequest):
    msg_id: int
    d: bytes
    conn: ISocketConnection = None

    def get_msg_id(self) -> int:
        return self.msg_id

    def get_d(self) -> bytes:
        return self.d

    def get_conn(self) -> ISocketConnection:
        return self.conn

    def set_conn(self, conn: ISocketConnection):
        self.conn = conn


@dataclass_json
@dataclass
class Response(IResponse):
    msg_id: int
    d: bytes

    def get_msg_id(self) -> int:
        return self.msg_id

    def get_d(self) -> bytes:
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

    def unpack(self, bytes_data) -> (IRequest, int):
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
