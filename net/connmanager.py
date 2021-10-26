from twisted.internet import reactor
from dataclasses import dataclass


@dataclass
class Request:
    # 消息id
    msg_id: int
    # 数据
    data: bytes
    # 连接
    conn: "Connection" = None

    def set_conn(self, conn: "Connection"):
        self.conn = conn


@dataclass
class Response:
    # 消息id
    msg_id: int
    # body
    body: bytes


class Connection:
    def __init__(self, proto):
        self.protocol = proto

    def lose_connection(self):
        self.protocol.transport.lostConnection()

    def write(self, data: bytes):
        reactor.callFromThread(self.protocol.transport.write, data)

    def send_response(self, *responses):
        for response in responses:
            self.write(self.protocol.factory.datapack.pack_response(response))

    @property
    def id(self):
        return self.protocol.transport.sessionno


class ConnectionManager:

    def __init__(self):
        # 所有的连接数据
        self._connections = {}

    def get_conns_cnt(self) -> int:
        # 当前连接数
        return len(self._connections)

    def add_conn(self, proto):
        conn = Connection(proto)
        # 添加连一个新的连接
        if conn.id in self._connections:
            return

        self._connections[conn.id] = conn

    def remove_conn_by_id(self, pk):
        # 移除一个连接
        try:
            del self._connections[pk]
        except KeyError:
            pass

    def get_conn_by_id(self, pk):
        return self._connections.get(pk)

    def sendto_sessions(self, response, send_list):
        """根据会话id，发送给这些连接数据"""
        for pk in send_list:
            if pk not in self._connections:
                continue

            try:
                self._connections[pk].send_msg(response)
            except:
                pass

    def sendto_all(self, response):
        self.sendto_sessions(response, self._connections.keys())

    def close_all(self):
        for conn in list(self._connections.values()):
            try:
                conn.lose_connection()
            except:
                pass
