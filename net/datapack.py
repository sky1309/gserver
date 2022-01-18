import enum
import struct
from typing import Union


def get_head_format(length, little_endian=False):
    head = "<" if little_endian else ">"
    if length == 2:
        s = "H"
    else:
        s = "I"
    return head + s


class EUnpackState(enum.IntEnum):
    OK = 0
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

    def pack(self, message: bytes) -> bytes:
        """打包数据"""
        return self.head_struct.pack(len(message)) + message

    def unpack(self, data: bytes) -> (bytes, Union[int, EUnpackState]):
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
            return None, int(EUnpackState.LENGTH_OVER)

        # 本条数据的结束为止
        end_index = head_length + message_length
        # 如果数据还没有接受完毕，那么久先不处理
        if data_length < end_index:
            return None, int(EUnpackState.LENGTH_NOT_ENOUGH)

        return data[head_length:end_index], end_index

    def get_head_len(self):
        """获取协议头的长度
        """
        return self.head_struct.size
