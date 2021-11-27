import threading
from dataclasses import dataclass
from typing import Optional
from twisted.internet import protocol

from log import log

from net.connmanager import ConnectionManager
from net.datapack import DataPack, EUnpackState


@dataclass
class FactoryConfig:
    """tcp服务配置"""
    port: int
    # 最大连接数
    max_connection_num: int = 1024


class ServerProtocol(protocol.Protocol):

    def __init__(self):
        # 接受缓冲区
        self._recv_buffer = b""
        # 写锁、发送缓冲区
        self._read_lock = threading.Lock()
        self._data_handler = None

    def connectionMade(self):
        if self.factory.conn_manager.get_conns_cnt() >= self.factory.config.max_connection_num:
            log.lgserver.warning(f"max client online, max={self.factory.config.max_connection_num}!")
            self.transport.loseConnection()
            return

        # 收到socket连接后创建一个连接对象
        conn_str = "*** new conn: total: {}, sid: {}, addr: {} ***".format(
            self.factory.conn_manager.get_conns_cnt(), self.transport.sessionno, self.transport.hostname)
        print("-" * len(conn_str))
        print(conn_str)
        print("-" * len(conn_str))

        # 添加一个新的连接 && 调用 connection的on_start方法
        self.factory.conn_manager.add_conn(self)

        self._data_handler = self._data_handle_coroutine()
        self._data_handler.send(None)

    def connectionLost(self, reason=protocol.connectionDone):
        """conn 关闭，手动调用也可以，这个函数执行了，就会把连接给关闭了
        """
        print("[conn {}] closed!".format(self.transport.sessionno))
        # 关闭携程(携程可能没有创建)
        if self._data_handler:
            self._data_handler.close()

        # 客户端关闭连接的时候会调用
        self.factory.do_conn_lost(self.factory.conn_manager.get_conn_by_id(self.transport.sessionno))

        # 删除找个连接
        self.factory.conn_manager.remove_conn_by_id(self.transport.sessionno)

    def dataReceived(self, data):
        self._data_handler.send(data)

    def _parse_row(self):
        # 读取一行的数据（一条有效的数据）
        request, offset = self.factory.datapack.unpack(self._recv_buffer)

        # 如果读到了数据，那么需要处理
        if request:
            with self._read_lock:
                self._recv_buffer = self._recv_buffer[offset:]
        else:
            # 没有解析到数据，判断是否出现了错误
            if offset == EUnpackState.LENGTH_OVER:
                # 发送的数据太长了，断开连接
                self.transport.loseConnection()

        return request

    def _data_handle_coroutine(self):
        """读取数据的时候"""
        head_length = self.factory.datapack.get_head_len()
        while True:
            d = yield
            # 没有需要接受接受的数据了，跳过
            self._recv_buffer += d

            requests = list()
            while len(self._recv_buffer) >= head_length:
                request = self._parse_row()
                if not request:
                    break

                request.set_conn(self.factory.conn_manager.get_conn_by_id(self.transport.sessionno))
                requests.append(request)
                # 如果 requests 中量很大了，先扔到处理的队列中去

            # 处理消息
            self.factory.deal_requests(*requests)


class ServerFactory(protocol.Factory):
    protocol = ServerProtocol
    # 连接管理
    conn_manager = ConnectionManager()
    # 数据解析
    datapack = None
    # 消息处理
    service = None
    # 连接断开的回调
    conn_lost_callback = None
    # *** 配置
    config: Optional[FactoryConfig] = None

    def startFactory(self):
        if not self.datapack:
            self.datapack = DataPack()

    def deal_requests(self, *requests):
        """处理请求处理"""
        if not self.service:
            log.lgserver.warning("factory not set message handler!")
            return
        self.service.handle_requests(*requests)

    def do_conn_lost(self, conn):
        if self.conn_lost_callback is None:
            return
        self.conn_lost_callback(conn)
