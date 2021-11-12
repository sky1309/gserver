import threading
from twisted.internet import protocol, reactor

from config.globalconfig import SERVER_CONFIG

from net.connmanager import ConnectionManager
from net.datapack import DataPack
from net.msghandler import msg_handler


class ServerProtocol(protocol.Protocol):

    def __init__(self, *args, **kwargs):
        super(ServerProtocol, self).__init__(*args, **kwargs)

        # 接受缓冲区
        self._recv_buffer = b""
        # 写锁、发送缓冲区
        self._read_lock = threading.Lock()
        self._data_handler = None

    def connectionMade(self):
        if self.factory.conn_manager.get_conns_cnt() >= SERVER_CONFIG.max_connection_num:
            self.transport.lostConnection()
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
        # 关闭携程
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
            self.factory.msg_handler.add_to_task_queue(*requests)

    def delay_close(self):
        # 延迟关闭conn
        reactor.callFromThread(self.transport.loseConnection)


class ServerFactory(protocol.Factory):
    protocol = ServerProtocol
    # 连接管理
    conn_manager = ConnectionManager()
    # 数据解析
    datapack = DataPack()
    # 消息处理
    msg_handler = msg_handler
    # 连接断开的回调
    conn_lost_callback = None

    def startFactory(self):
        # 开启消息处理队列
        self.msg_handler.start()

    def stopFactory(self):
        self.msg_handler.stop()

    def do_conn_lost(self, conn):
        if self.conn_lost_callback is None:
            return

        self.conn_lost_callback(conn)
