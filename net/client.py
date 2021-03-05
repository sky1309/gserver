from iface import ISocketConnection
from iface.iclient import IClient


class Client(IClient):
    def __init__(self, conn: ISocketConnection):
        self._conn = conn

    def get_conn(self) -> ISocketConnection:
        return self._conn

    def set_conn(self, conn: ISocketConnection):
        self._conn = conn
