import enum
import struct

from log import log

from .connmanager import Request, Response


class EUnpackState(enum.IntEnum):
    # 长度不足
    LENGTH_NOT_ENOUGH = -1
    # 长度超了
    LENGTH_OVER = -2


class DataPack:
    # 最大数据包的大小
    package_max_size = 2 ** 16 - 1

    def __init__(self, fmt=">H", message_id_fmt=">H"):
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
        if message_length > self.package_max_size:
            log.lgserver.warning(f"invalid package size:{message_length}, expect lte:{self.package_max_size}!")
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
