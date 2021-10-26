import yaml
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass
class Config(DataClassJsonMixin):
    # 端口号
    PORT: int = 3636
    BACKLOG: int = 20

    # # 最大连接数
    MAX_CONNECTION_NUM: int = 1024
    # msg handler 处理线程数
    WORKER_POOL_SIZE: int = 5
    # 最大数据包的大小
    PACKAGE_MAX_SIZE: int = 2 ** 16

    # socket数据长度格式，">H" 表示short int 2个字节，# 0x0002 0x0002 0x1234
    DEFAULT_FMT: str = ">I"
    # 消息id占用两个字节
    DEFAULT_MESSAGE_ID_FMT = ">H"
    # # 是否使用加密
    enable_crypt: bool = True

    def reload(self, file_path: str):
        """重新加载配置文件到全局的Config对象中去"""
        # 重新加载配置文件

        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        for key, t in self.__annotations__.items():
            if not (key in data and isinstance(data[key], t)):
                continue
            setattr(self, key, data[key])


# 全局的配置对象, 配置服务启动的情况
SERVER_CONFIG = Config()
