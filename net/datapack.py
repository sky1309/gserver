import enum
import struct

from log import log

from .connmanager import Request, Response


def get_head_format(length, little_endian=False):
    head = "<" if little_endian else ">"
    if length == 2:
        s = "H"
    else:
        s = "I"
    return head + s


class EUnpackState(enum.IntEnum):
    # 长度不足
    LENGTH_NOT_ENOUGH = -1
    # 长度超了
    LENGTH_OVER = -2


class DataPack:

    def __init__(self, head_len=2, max_msg_len=65535, little_endian=False):
        """
        参数:
          - head_len: int 头包含几个字节
          - max_msg_len: int 一个数据包最大的大小
          - little_endian: bool 是否是小端，默认是大段，高位对齐
        """
        self.head_len = head_len
        # 一次最多接受的数据大小
        self.max_msg_len = max_msg_len
        self.little_endian = little_endian

        self.head_struct = struct.Struct(get_head_format(self.head_len, self.little_endian))
        self.message_id_struct = struct.Struct(get_head_format(2, self.little_endian))

    def set_head_len(self, head_len):
        # 设置头的长处，重新设置 self.head_struct
        self.head_len = head_len
        self.head_struct = struct.Struct(get_head_format(self.head_len, self.little_endian))

    def set_little_endian(self, little_endian=False):
        # 设置大小端
        if self.little_endian == little_endian:
            return
        self.little_endian = little_endian
        self.head_struct = struct.Struct(get_head_format(self.head_len, self.little_endian))
        self.message_id_struct = struct.Struct(get_head_format(2, self.little_endian))

    def pack(self, data: bytes) -> bytes:
        """打包数据"""
        return self.head_struct.pack(len(data)) + data

    def pack_response(self, response: Response):
        data = self.message_id_struct.pack(response.msg_id) + response.body
        return self.pack(data)

    def unpack(self, data: bytes) -> (Request, int):
        """解析接收到的数据
        返回值：(Optional[Request, int])
           解析成功 (Request, int)
           数据长度不足 (None, -1)
           数据过长 (None, 0)
        """
        data_length = len(data)
        head_length = self.get_head_len()
        # 数据没有接受完
        if data_length < head_length:
            return None, int(EUnpackState.LENGTH_NOT_ENOUGH)

        message_length, = self.head_struct.unpack_from(data, 0)
        if message_length > self.max_msg_len:
            log.lgserver.warning(f"invalid package size:{message_length}, expect lte:{self.max_msg_len}!")
            return None, int(EUnpackState.LENGTH_OVER)

        # 本条数据的结束为止
        end_index = head_length + message_length
        # 如果数据还没有接受完毕，那么久先不处理
        if data_length < end_index:
            return None, int(EUnpackState.LENGTH_NOT_ENOUGH)

        message_id, = self.message_id_struct.unpack_from(data, head_length)
        return Request(message_id, data[head_length + self.message_id_struct.size: end_index]), end_index

    def get_head_len(self):
        """获取协议头的长度
        """
        return self.head_struct.size
