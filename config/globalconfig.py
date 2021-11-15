import os
import json

from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass
class NodeConfig:
    """节点名称"""
    # pb端口号
    port: int
    # 服务名称
    name: str
    # 主机地址
    host: str = "0.0.0.0"


@dataclass
class NetConfig(DataClassJsonMixin):
    # 端口号
    port: int = 3636

    # # 最大连接数
    max_connection_num: int = 1024
    # msg handler 处理线程数
    worker_size: int = 5
    # 最大数据包的大小
    package_max_size: int = 2 ** 16

    # socket数据长度格式，">H" 表示short int 2个字节，# 0x0002 0x0002 0x1234
    default_fmt: str = ">I"
    # 消息id占用两个字节
    default_message_id_fmt = ">H"
    # 是否使用加密
    enable_crypt: bool = True

    @classmethod
    def from_config(cls, data) -> "NetConfig":
        """重新加载配置文件到全局的Config对象中去 config-template.json
        """
        return cls.from_dict(data)


def read_config_file(node_id, path="./config/config-template.json"):
    """重新读取配置文件"""
    _config_file_path = os.path.join(os.getcwd(), path)
    if not os.path.exists(_config_file_path):
        return

    with open(_config_file_path, "r") as f:
        data = json.load(f)

    return data["nodes"][node_id]


# 节点id
# 全局的配置对象, 配置服务启动的情况
NET_CONFIG = NetConfig()
