import os
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin

from util import file

# 配置文件路径项目启动目录下面 WORKSPACE/
config_path = os.path.join(os.getcwd(), "config/config.json")


@dataclass
class NodeInfo(DataClassJsonMixin):
    # 节点id
    node_id: int
    # 节点名称
    name: str
    # 地址
    host: str
    # 监听的端口，远程调用
    port: int


@dataclass
class NetConfig:
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

    def load_config(self, node_id):
        """加载配置文件"""
        config = file.load_json_file(config_path)

        # 只加载有的字段
        for key, value in config["gates"][str(node_id)].items():
            if key not in self.__annotations__:
                continue
            setattr(self, key, value)


# 节点id
# 全局的配置对象, 配置服务启动的情况（有的情况下是不使用gate服务的）
NET_CONFIG = NetConfig()
